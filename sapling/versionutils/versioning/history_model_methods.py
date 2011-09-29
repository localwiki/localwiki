"""
Attributes/methods of historical instances.

Because we are constructing our historical classes dynamically
we can't simply write down "class MyHistoricalInstance(..)..."
so we have the methods laid out flat here.
"""
import datetime
from functools import partial

from django.db import models
from django.db.models import Max
from django.utils.functional import SimpleLazyObject
from django.db.models.sql.constants import LOOKUP_SEP
from django.core.exceptions import ObjectDoesNotExist

from constants import *
from utils import *


def get_history_methods(self, model):
    """
    Returns a dictionary of the essential methods that will be added to
    the histoical record model.
    """
    fields = {
        # lookup function for cleaniness. Instead of doing
        # h.history_ip_address we can write h.version_info.ip_address
        'version_info': HistoricalMetaInfo(),
        'revert_to': revert_to,
        '__init__': historical_record_init,
        '__getattribute__':
            # not sure why functools.partial doesn't work here
            lambda m, name: historical_record_getattribute(model, m, name),
    }

    return fields


def get_history_fields(self, model):
    """
    Returns a dictionary of the essential fields that will be added to the
    historical record model, in addition to the ones returned by
    models.get_fields.

    Args:
        model: A model class.
    """
    fields = {
        'history_id': models.AutoField(primary_key=True),
        'history__object': HistoricalObjectDescriptor(model),
        'history__object_rel_populated': HistoricalObjectDescriptor(
            model, populate_related=True),
        'history_date': models.DateTimeField(default=datetime.datetime.now),
        'history_version_number': version_number_of,
        'history_type': models.SmallIntegerField(choices=TYPE_CHOICES),
        'history_type_verbose': type_to_verbose,
        # If you want to display "Reverted to version N" in every change
        # comment then you should stash that in the comment field
        # directly rather than using
        # reverted_to_version.version_number() on each display.
        'history_reverted_to_version': models.ForeignKey('self', null=True),
    }

    return fields


def type_to_verbose(m):
    return TYPE_CHOICES[m.version_info.type][1]


def historical_record_init(m, *args, **kws):
    """
    This is the __init__ method of historical record instances.
    """
    if kws.get('__class__'):
        base = kws.get('__class__').__base__
    else:
        base = m.__class__.__base__

    if is_historical_instance(base):
        kws['__class__'] = base
    else:
        if kws.get('__class__'):
            del kws['__class__']

    retval = base.__init__(m, *args, **kws)
    m._wrapped_lookup_fields = {}
    _wrap_reverse_lookups(m)
    return retval


def _wrap_reverse_lookups(m):
    """
    Make reverse foreign key lookups return historical versions
    if the model is versioned.

    Args:
        m: A historical record instance.
    """
    def _reverse_set_lookup(m, rel_o):
        attr = rel_o.field.name
        parent_model = rel_o.model
        as_of = m.version_info.date
        parent_pk_att = parent_model._meta.pk.attname

        # Find unique fields of the base (non-historical) model
        # or use the pk.  We use unique fields, if available, because
        # the underlying pk can change through delete -> recreation
        # cycles while the unique fields stay the same.
        unique_values = unique_lookup_values_for(m.version_info._object)
        if not unique_values:
            pk_att = m.version_info._object._meta.pk.attname
            pk_val = getattr(m.version_info._object, pk_att)
            unique_values = {pk_att: pk_val}

        # Construct something like {'b__email':'a@example.org', ...}
        # from the unique fields of the base model.
        new_unique_values = {}
        for k, v in unique_values.iteritems():
            new_unique_values['%s%s%s' % (attr, LOOKUP_SEP, k)] = v
        unique_values = new_unique_values

        # Grab parent history objects that are less than the as_of date
        # that point at the base model.
        qs = get_versions(parent_model).filter(
            history_date__lte=as_of,
            **unique_values
        )
        # Then group by the parent_pk
        qs = qs.order_by(parent_pk_att).values(parent_pk_att).distinct()
        # then annotate the maximum history object id
        ids = qs.annotate(Max('history_id'))
        history_ids = [v['history_id__max'] for v in ids]
        # return a QuerySet containing the proper history objects
        return get_versions(parent_model).filter(history_id__in=history_ids)

    def _reverse_attr_lookup(m, rel_o):
        attr = rel_o.field.name
        parent_model = rel_o.model
        as_of = m.version_info.date
        is_subclass = False

        # Find unique values of the base (non-historical) model.
        unique_values = unique_lookup_values_for(m.version_info._object)
        if not unique_values:
            # Check to see if this is a subclass relation with a
            # historical model.
            for k, v in rel_o.opts.parents.iteritems():
                if is_versioned(k):
                    # Cheap comparison hack.
                    is_subclass = v.related.__dict__ == rel_o.__dict__

            pk_att = m.version_info._object._meta.pk.attname
            if is_subclass:
                # For subclassed historical models' implicit OneToOne
                # relation we want to use the id of the historical
                # model when the related object is also versioned.
                pk_val = getattr(m, 'history_id')
            else:
                pk_val = getattr(m.version_info._object, pk_att)
            unique_values = {pk_att: pk_val}

        # Construct something like {'b__email':'a@example.org', ...}
        # from the unique fields of the base model.
        new_unique_values = {}
        for k, v in unique_values.iteritems():
            new_unique_values['%s%s%s' % (attr, LOOKUP_SEP, k)] = v
        unique_values = new_unique_values

        try:
            obj = get_versions(parent_model).filter(
                history_date__lte=as_of,
                **unique_values
            )[0]
        except IndexError:
            raise getattr(parent_model, hist_name).model.DoesNotExist(
                "%s matching query does not exist." %
                getattr(parent_model, hist_name).model._meta.object_name)
        return obj

    model_meta = m.version_info._object._meta
    related_objects = model_meta.get_all_related_objects()
    related_objects += model_meta.get_all_related_many_to_many_objects()
    related_versioned = [o for o in related_objects if is_versioned(o.model)]
    for rel_o in related_versioned:
        # Set the accessor to a lazy lookup function that, when
        # accessed, looks up the proper related set.
        accessor = rel_o.get_accessor_name()

        if isinstance(rel_o.field, models.OneToOneField):
            # OneToOneFields have a direct lookup (not a set).
            _reverse_lookup = partial(_reverse_attr_lookup, m, rel_o)
        else:
            _reverse_lookup = partial(_reverse_set_lookup, m, rel_o)
        m._wrapped_lookup_fields[accessor] = SimpleLazyObject(_reverse_lookup)


def historical_record_getattribute(model, m, name):
    """
    We have to define our own __getattribute__ because otherwise there's
    no way to set our wrapped foreign key attributes.  We also use this
    function to do a 'fallback' lookup on methods and attributes on the
    non-historical instance.

    If we try and set
    history_instance.att = SimpleLazyObject(_lookup_proper_fk_version)
    we'll get an error because Django does an isinstance() check on
    assignment to model fields. Additionally, the __set__ method on
    related fields will force evaluation due to equality checks.

    Args:
        model: A model class.
        m: The model instance.
        name: The string representing the attribute name.
    """
    basedict = model.__getattribute__(m, '__dict__')
    direct_val = basedict.get('_wrapped_lookup_fields', {}).get(name)
    if direct_val is not None:
        return direct_val
    # We allow the original attribute to be obtained by asking for
    # m.__direct_name.
    if name.startswith('__direct_'):
        name = name[9:]

    try:
        callables = model.__getattribute__(m, '_original_callables')
    except AttributeError:
        pass
    else:
        if name in callables:
            # This is a callable so let's do a lookup on the non-historical
            # model instance.
            return m.version_info._object_rel_populated.__getattribute__(name)
    return model.__getattribute__(m, name)


def _cascade_revert(current_hm, m, **kws):
    """
    Iterates through (reverse) related objects and calls revert_to() on
    them if they were deleted via a cascaded delete.
    """
    version_before_delete = current_hm.version_info.version_number() - 1

    hm = get_versions(m).as_of(version=version_before_delete)

    related_objs_versioned = [
        o for o in m._meta.get_all_related_objects() if is_versioned(o.model)
    ]
    for rel_o in related_objs_versioned:
        rel_lookup = getattr(hm, '__direct_%s_hist_set' % rel_o.var_name)
        if rel_lookup:
            rel_hms = rel_lookup.all()
        else:
            # A direct value (e.g. OneToOne).
            rel_lookup = getattr(hm, '__direct_%s_hist' % rel_o.var_name)
            rel_hms = [rel_lookup]

        for rel_hm in rel_hms:
            latest_rel_hm = get_versions(
                rel_hm.version_info._object).most_recent()
            if latest_rel_hm.version_info.type in [TYPE_DELETED_CASCADE,
                    TYPE_REVERTED_DELETED_CASCADE]:
                # The related object was most recently deleted via a
                # delete cascade.  So we revert it.
                latest_rel_hm._from_cascade_revert = True
                latest_rel_hm.revert_to(**kws)


def revert_to(hm, delete_newer_versions=False, **kws):
    """
    This is used on a *historical instance* - e.g. something you get
    using history.get(..) rather than an instance of the model.  Like::

        >> ph = p.versions.as_of(..)
        >> ph.revert_to()

    Reverts to this version of the model.

    Args:
        delete_newer_versions: If True, delete all versions in the
            history newer than this version.
        track_changes: If False, won't log *this revert* as an action in
            the history log.
        kws: Any other keyword arguments you want to pass along to the
            model save method.

    Returns:
        The new model instance.
    """
    m = hm.version_info._object

    # If we simply save hm.version_info._object we may hit a uniqueness
    # exception.  If we save the model and it already exists.  This is because
    # the pk of the model may have changed if it was deleted at some time.

    # Get the current model instance if it exists and set the pk
    # accordingly.
    unique_values = unique_lookup_values_for(m)
    if unique_values:
        ms = m.__class__.objects.filter(**unique_values)
        if ms:
            # Keep the primary key unique.
            m.pk = ms[0].pk

    if delete_newer_versions:
        newer = get_versions(m).filter(
            version_info__date__gt=hm.version_info.date)
        for v in newer:
            v.delete()

    m._history_type = TYPE_REVERTED

    # Having the _from_cascade_revert attribute means revert_to() was
    # called from _cascade_revert().
    if getattr(hm, '_from_cascade_revert', False):
        m._history_type = TYPE_REVERTED_CASCADE

    if hm.version_info.type == TYPE_DELETED:
        # Delete the model when reverting to a deleted version.
        m.delete(reverted_to_version=hm, **kws)
    else:
        # Check that none of the attached, versioned related fields are
        # currently deleted.
        for field in get_related_versioned_fields(m):
            rel_hist = getattr(hm, field.name)
            rel_o = rel_hist.version_info._object
            latest_version = get_versions(rel_o).most_recent()
            if latest_version.version_info.type == TYPE_DELETED:
                # This means the related, versioned object is
                # currently deleted.  In this case we want to throw
                # an exception, as reverting doesn't make any sense
                # and will otherwise raise a database
                # IntegrityError.
                raise ObjectDoesNotExist("Model attribute '%s' points to "
                    "model %s that does not exist! Re-create the "
                    "referenced model and try again." %
                    (field.name, rel_o.__class__))

        current_hm = get_versions(m).most_recent()

        m.save(reverted_to_version=hm, **kws)

        # If we are reverting from a deleted state to a restored state
        # then we should cascade the revert to children that were
        # deleted during the initial delete().
        if current_hm.version_info.type in DELETED_TYPES:
            _cascade_revert(current_hm, m, **kws)

    return m


def version_number_of(hm):
    """
    Returns version number.

    Args:
        hm: Historical record instance.
    """
    if getattr(hm.version_info.instance, '_version_number', None) is None:
        date = hm.version_info.date
        obj = hm.version_info._object
        hm.version_info.instance._version_number = len(
            get_versions(obj).filter(history_date__lte=date)
        )
    return hm.version_info.instance._version_number


class HistoricalMetaInfo(object):
    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def __getattr__(self, name):
        try:
            return getattr(self.__dict__['instance'], 'history_%s' % name)
        except AttributeError, s:
            raise AttributeError("version_info has no attribute %s" % name)

    def __setattr__(self, name, val):
        if name == 'instance':
            self.__dict__['instance'] = val
            return
        try:
            self.__dict__['instance'].__setattr__('history_%s' % name, val)
        except AttributeError, s:
            raise AttributeError("version_info has no attribute %s" % name)


class HistoricalObjectDescriptor(object):
    def __init__(self, model, populate_related=False):
        self._populate_related = populate_related
        self.model = model

    def populate_related(self, m, instance):
        # We set all related, versioned attributes to their
        # non-versioned *instance* form.  We don't just look them up --
        # we create the instances.  This makes 'if related..' step
        # in __get__ redundant, but we need to create the model before
        # we can do this and in order to create the model we need to
        # pass it something.
        for f in self.model._meta.fields:
            related = getattr(f, 'related', None)
            if related and is_versioned(related.parent_model):
                attribute = getattr(instance, f.name)
                related_direct_obj = attribute.version_info._object
                setattr(m, f.name, related_direct_obj)
        return m

    def __get__(self, instance, owner):
        values = []
        for f in self.model._meta.fields:
            related = getattr(f, 'related', None)
            if related and is_versioned(related.parent_model):
                # If the field points to a related, versioned model then
                # we need to subsitute a pk to an instance of that model
                # not versioned) here.  This is because we use the same
                # attname for the pointer to the historical, related
                # object.  For instance, if we have "Map" -> OneToOne ->
                # "Page", then in Map_hist we have page_id which stores
                # the value of the Page_hist object.
                attribute = getattr(instance, f.name)
                if attribute is not None:
                    values.append(attribute.version_info._object.pk)
                else:
                    values.append(None)
            else:
                values.append(getattr(instance, f.attname))
        m = self.model(*values)
        if self._populate_related:
            m = self.populate_related(m, instance)
        return m
