import copy
from functools import partial

from django.db import models
from django.db.models.options import DEFAULT_NAMES as ALL_META_OPTIONS

from utils import *
from storage import *
from constants import *
from history_model_methods import get_history_fields
from history_model_methods import get_history_methods
import fields
import manager


class TrackChanges(object):
    def contribute_to_class(self, cls, name):
        self.manager_name = name
        models.signals.class_prepared.connect(self.finalize, sender=cls)

    def finalize(self, sender, **kws):
        if sender._meta.abstract:
            # We can't do anything on the abstract model.
            return
        elif sender._meta.proxy:
            # Get the history model from the base class.
            base = sender
            while base._meta.proxy:
                base = base._meta.proxy_for_model
            if hasattr(base, '_history_manager_name'):
                hist_attr = getattr(base, '_history_manager_name')
                history_model = getattr(sender, hist_attr).model
        else:
            history_model = self.create_history_model(sender)

        setattr(sender, '_track_changes', True)

        # Over-ride the save, delete methods to allow arguments to be passed in
        # such as comment="Made a small change."
        setattr(sender, 'save', save_func(sender.save))
        setattr(sender, 'delete', delete_func(sender.delete))

        # We also attach signal handlers to the save, delete methods.  It's
        # easier to have two things going on (signal, and an overridden method)
        # because the signal handlers tell us if the object is new or not.
        # (Just checking object.pk is None is not enough!)
        # Signal handlers are called when a bulk QuerySet.delete()
        # is issued -- custom delete() and save() methods aren't called
        # in that case.

        _post_save = partial(self.post_save, sender)
        _pre_delete = partial(self.pre_delete, sender)
        _post_delete = partial(self.post_delete, sender)
        # The TrackChanges object will be discarded, so the signal handlers
        # can't use weak references.
        models.signals.post_save.connect(
            _post_save, weak=False
        )
        models.signals.pre_delete.connect(
            _pre_delete, weak=False
        )
        models.signals.post_delete.connect(
            _post_delete, weak=False
        )

        self.wrap_model_fields(sender)

        descriptor = manager.HistoryDescriptor(history_model)
        setattr(sender, self.manager_name, descriptor)
        # Being able to look this up is intensely helpful.
        setattr(sender, '_history_manager_name', self.manager_name)

    def ineligible_for_history_model(self, model):
        """
        Certain abstract-y models can't have corresponding history models.
        """
        return model._meta.proxy or model._meta.abstract

    def create_history_model(self, model):
        """
        Creates a historical model to associate with the model provided.

        See http://code.djangoproject.com/wiki/DynamicModels
        Django 'sees' this new historical model class and actually creates a
        new model in the database (on syncdb) named <originalmodel>_hist.
        This happens because the class that's returned is just like a normal
        model definition ('class MyModel(models.Model)') in the eyes of the
        Django machinery.

        Returns:
            Class representing the historical version of the model.
        """
        # For convience's sake, it's nice to be able to reference the
        # non-historical class from the historical class.
        attrs = {
            '_original_model': model,
            # Though not strictly a field, this attribute
            # is required for a model to function properly.
            '__module__': model.__module__,
        }

        attrs.update(get_history_methods(self, model))
        # Parents mean we are concretely subclassed.
        if not model._meta.parents:
            attrs.update(self.get_misc_members(model))
            attrs.update(Meta=type('Meta', (), self.get_meta_options(model)))
        if not is_versioned(model.__base__):
            attrs.update(get_history_fields(self, model))
            attrs.update(self.get_extra_history_fields(model))
        attrs.update(self.get_fields(model))

        name = '%s_hist' % model._meta.object_name
        # If we have a parent (meaning we're concretely subclassing)
        # then let's have our historical object subclass the parent
        # model's historical model, if the parent model is versioned.
        # Concretely subclassed models keep some of their information in
        # their parent model's table, and so if we subclass then we can
        # mirror this DB relationship for our historical models.
        # Migrations are easier this way -- you migrate historical
        # models in the exact same fashion as non-historical models.
        if model._meta.parents:
            if is_versioned(model.__base__):
                return type(name, (model.__base__.history.model,), attrs)
            return type(name, (model.__base__,), attrs)
        return type(name, (models.Model,), attrs)

    def wrap_model_fields(self, model):
        """
        Wrap some of the model's fields to add extra behavior.
        """
        for field in model._meta.fields:
            if isinstance(field, models.FileField):
                field.storage = FileStorageWrapper(field.storage)

    MEMBERS_TO_SKIP = [
        '__dict__',
        '__module__',
        '__weakref__',
        # TODO, maybe: if we wanted to be fancy we could define our
        # own __doc__ that explains "this is like the normal model
        # plus these historical methods."
        '__doc__',
        '_meta',
        '_base_manager',
        '_default_manager',
        'save',
        'delete'
    ]

    FK_FIELDS_TO_COPY = [
        'null',
        'blank',
        'db_index',
        'db_tablespace',
        'to_field'
    ]

    M2M_FIELDS_TO_COPY = [
        'null',
        'blank',
        'db_index',
        'db_tablespace',
    ]

    def get_misc_members(self, model):
        # Would like to know a better way to do this.
        # Ideally we would subclass the model and then extend it,
        # but Django won't let us replace a field (in our case, a
        # ForeignKey field change to point to a historical model).
        # See also http://bit.ly/9k2Eqn
        #
        # The error we see when trying this is:
        # FieldError: Local field 'person' in class 'ProfileChangeFK' clashes
        # with field of similar name from base class 'Profile'
        #
        # But really -- even though the historical model does a good job
        # of pretending to be the non-historical model -- it's still a
        # different model.  Faking might be bad.  People shouldn't write code
        # that depends on the model type.  If this becomes problematic then
        # we can swap out our call to type() in create_history_model()
        # for a call to a metaclass with __instancecheck__ /
        # __subclasscheck__ defined (a'la python 2.6)
        d = copy.copy(dict(model.__dict__))
        for k in TrackChanges.MEMBERS_TO_SKIP:
            if d.get(k, None) is not None:
                del d[k]
        # Modify fields and remove some fields we know we'll re-add in
        # modified form later.
        for k in copy.copy(d):
            if isinstance(d[k], models.fields.Field):
                del d[k]
                continue
            # This appears with model inheritance.
            elif isinstance(getattr(d[k], 'field', None), models.fields.Field):
                del d[k]
                continue
            if isinstance(getattr(d[k], 'manager', None), models.Manager):
                # Re-init managers.
                d[k] = d[k].manager.__class__()
        return d

    def get_fields(self, model):
        """
        Creates copies of the model's original fields.

        Returns:
            A dictionary mapping field name to copied field object.
        """
        def _get_fk_opts(field):
            opts = {}
            for k in TrackChanges.FK_FIELDS_TO_COPY:
                if hasattr(field, k):
                    opts[k] = getattr(field, k, None)
            return opts

        def _get_m2m_opts(field):
            # Always set symmetrical to False as there's no disadvantage
            # to allowing reverse lookups.
            opts = {'symmetrical': False}
            for k in TrackChanges.M2M_FIELDS_TO_COPY:
                if hasattr(field, k):
                    opts[k] = getattr(field, k, None)
            # XXX TODO deal with intermediate tables
            if hasattr(field, 'through'):
                pass
            return opts

        attrs = {}
        for field in (model._meta.local_fields +
                      model._meta.local_many_to_many):
            field = copy.deepcopy(field)

            if isinstance(field, models.AutoField):
                # The historical model gets its own AutoField, so any
                # existing one must be replaced with an IntegerField.
                field.__class__ = models.IntegerField
                field.serialize = True

            if field.primary_key or field.unique:
                # Unique fields can no longer be guaranteed unique,
                # but they should still be indexed for faster lookups.
                field.primary_key = False
                field._unique = False
                field.db_index = True

            if getattr(field, 'auto_now', None):
                # Don't set auto_now=True historical models' fields.
                field.auto_now = False

            is_fk = isinstance(field, models.ForeignKey)
            is_m2m = isinstance(field, models.ManyToManyField)
            if is_fk or is_m2m:
                parent_model = field.related.parent_model
                is_to_self = parent_model == model
                # If the field is versioned then we replace it with a
                # FK/M2M to the historical model.
                if is_versioned(parent_model) or is_to_self:
                    if getattr(field.rel, 'parent_link', None):
                        # Concrete model inheritance and the parent is
                        # versioned.  In this case, we subclass the
                        # parent historical model and use that parent
                        # related field instead.
                        continue
                    if is_fk:
                        model_type = models.ForeignKey
                        options = _get_fk_opts(field)
                    else:
                        model_type = models.ManyToManyField
                        options = _get_m2m_opts(field)
                        _m2m_changed = partial(self.m2m_changed, field.attname)
                        models.signals.m2m_changed.connect(_m2m_changed,
                            sender=getattr(model, field.attname).through,
                            weak=False,
                        )
                    if is_to_self:
                        # Fix related name conflict. We set this manually
                        # elsewhere so giving this a funky name isn't a
                        # problem.
                        options['related_name'] = ('%s_hist_set_2' %
                            field.related.var_name)
                        hist_field = model_type('self', **options)
                    else:
                        # Make the field into a foreignkey pointed at the
                        # history model.
                        fk_hist_obj = field.related.parent_model.history.model
                        hist_field = model_type(fk_hist_obj, **options)

                    hist_field.name = field.name
                    hist_field.attname = field.attname
                    field = hist_field

            attrs[field.name] = field

        return attrs

    def get_extra_history_fields(self, model):
        """
        Extra, non-essential fields for the historical models.

        If you subclass TrackChanges this is a good method to over-ride:
        simply add your own values to the fields for custom fields.

        NOTE: Your custom fields should start with history_ if you want them
              to be looked up via hm.history_info.fieldname

        Returns:
            A dictionary of fields that will be added to the historical
            record model.
        """
        attrs = {
            'history_comment': models.CharField(max_length=200, blank=True,
                                                null=True
            ),
            'history_user': fields.AutoUserField(null=True),
            'history_user_ip': fields.AutoIPAddressField(null=True),
            '__unicode__': lambda self: u'%s as of %s' % (self.history__object,
                                                          self.history_date)
        }
        return attrs

    META_TO_SKIP = [
        'db_table', 'get_latest_by', 'managed', 'unique_together', 'ordering',
    ]

    def get_meta_options(self, model):
        """
        Returns:
            A dictionary of fields that will be added to the Meta inner
            class of the historical record model.
        """
        meta = {'ordering': ('-history_date',)}
        for k in ALL_META_OPTIONS:
            if k in TrackChanges.META_TO_SKIP:
                continue
            meta[k] = getattr(model._meta, k)
        return meta

    def post_save(self, parent, instance, created, **kws):
        # To support subclassing.
        if not isinstance(instance, parent):
            return
        parent_instance = get_parent_instance(instance, parent)
        if parent_instance:
            if (is_versioned(parent_instance) and
                is_directly_versioned(instance)):
                # The parent instance has its own handler that will fire
                # in this case.
                return
            # Because this signal is attached to the parent
            # class, let's save a historical record for the
            # parent instance here.
            instance = parent_instance

        history_type = getattr(instance, '_history_type', None)
        is_revert = history_type == TYPE_REVERTED
        if created:
            history_type = TYPE_REVERTED_ADDED if is_revert else TYPE_ADDED
        else:
            history_type = history_type or TYPE_UPDATED
        hist_instance = self.create_historical_record(instance, history_type)
        self.m2m_init(instance, hist_instance)

    def pre_delete(self, parent, instance, **kws):
        # To support subclassing.
        if not isinstance(instance, parent):
            return
        parent_instance = get_parent_instance(instance, parent)
        if parent_instance:
            if is_versioned(parent_instance):
                # The parent instance has its own handler that will fire
                # in this case.
                return
            # Because this signal is attached to the parent
            # class, let's save a historical record for the
            # parent instance here.
            instance = parent_instance

        self._pk_recycle_cleanup(instance)

        # If this model has a parent model (concrete model inheritance)
        # and that model isn't versioned then we need to set
        # track_changes=False.  This is because the parent model is
        # considered a 'part' of the child model in this case and this
        # is the only way to ensure consistency.
        for model in instance.__class__._meta.parents:
            if not is_versioned(model):
                instance._track_changes = False

    def post_delete(self, parent, instance, **kws):
        # To support subclassing.
        if not isinstance(instance, parent):
            return

        parent_instance = get_parent_instance(instance, parent)
        if parent_instance:
            if is_versioned(parent_instance):
                # The parent instance has its own handler that will fire
                # in this case.
                return
            # Because this signal is attached to the parent
            # class, let's save a historical record for the
            # parent instance here.
            instance = parent_instance

        history_type = getattr(instance, '_history_type', None)
        is_revert = history_type == TYPE_REVERTED
        history_type = TYPE_REVERTED_DELETED if is_revert else TYPE_DELETED
        if not is_pk_recycle_a_problem(instance) and instance._track_changes:
            hist_instance = self.create_historical_record(instance, history_type)
            self.m2m_init(instance, hist_instance)

        # Disconnect the related objects signals
        if hasattr(instance, '_rel_objs_methods'):
            for model, method in instance._rel_objs_methods.iteritems():
                models.signals.pre_delete.disconnect(method, model, weak=False)

    def m2m_init(self, instance, hist_instance):
        """
        Initialize the ManyToMany sets on a historical instance.
        """
        for field in instance._meta.many_to_many:
            if is_versioned(field.related.parent_model):
                current_objs = getattr(instance, field.attname).all()
                setattr(hist_instance, field.attname,
                        [o.history.most_recent() for o in current_objs]
                )

    def m2m_changed(self, attname, sender, instance, action, reverse,
                    model, pk_set, **kwargs):
        """
        A signal handler that syncs changes to m2m relations with
        historical models.

        Args:
            attname: Attribute name of the m2m field on the base model.
        """
        if pk_set:
            changed_ms = [model.objects.get(pk=pk) for pk in pk_set]
            hist_changed_ms = [m.history.most_recent() for m in changed_ms]
        hist_instance = instance.history.most_recent()
        hist_through = getattr(hist_instance, attname)
        if action == 'post_add':
            for hist_m in hist_changed_ms:
                hist_through.add(hist_m)
        elif action == 'post_remove':
            for hist_m in hist_changed_ms:
                hist_through.remove(hist_m)
        elif action == 'post_clear':
            hist_through.clear()

    def create_historical_record(self, instance, type):
        manager = getattr(instance, self.manager_name)
        # If they set track_changes to False
        # then we don't auto-create a revision here.
        if not instance._track_changes:
            return
        attrs = {}
        for field in instance._meta.fields:
            if isinstance(field, models.fields.related.ForeignKey):
                is_fk_to_self = (field.related.parent_model ==
                                 instance.__class__)
                if is_versioned(field.related.parent_model) or is_fk_to_self:
                    if field.rel.parent_link:
                        # Concrete model inheritance and the parent is
                        # versioned.  In this case, we subclass the
                        # parent historical model and use that parent
                        # related field instead.
                        continue

                    # If the FK field is versioned, set it to the most
                    # recent version of that object.
                    # The object the FK id refers to may have been
                    # deleted so we can't simply do Model.objects.get().
                    fk_hist_model = field.rel.to.history.model
                    fk_id_name = field.rel.field_name
                    fk_id_val = getattr(instance, field.attname)
                    fk_objs = fk_hist_model.objects.filter(
                        **{fk_id_name: fk_id_val}
                    )

                    if fk_objs:
                        attrs[field.name] = fk_objs[0]  # most recent version
                    else:
                        attrs[field.name] = None
                    continue

            attrs[field.attname] = getattr(instance, field.attname)

        attrs.update(self._get_save_with_attrs(instance))
        return manager.create(history_type=type, **attrs)

    def _get_save_with_attrs(self, instance):
        """
        Prefix all keys with 'history_' to save them into the history
        model correctly.
        """
        d = {}
        for k, v in getattr(instance, '_save_with', {}).iteritems():
            d['history_%s' % k] = v
        return d

    def _pk_recycle_cleanup(self, instance):
        """
        SQLite recycles autofield primary keys. Oops!
        This will be fixed eventually:
        Django Ticket #10164: http://code.djangoproject.com/ticket/10164

        As a temporary consistency fix, we zero-out history of deleted objects
        that lack unique fields to prevent history-mystery!  The alternative
        would be to throw an error on deletion of these objects.
        """
        if not is_pk_recycle_a_problem(instance):
            return

        manager = getattr(instance, self.manager_name)
        for entry in manager.all():
            entry.delete()


def _related_objs_delete_passalong(m):
    """
    For all related objects, set _track_changes and _save_with
    accordingly.

    Args:
        m: A model instance.
    """
    # We use signals here.  One alternative would be to do the
    # cascade ourselves, but we can't be sure of casade behavior.
    def _set_arguments_for(child_m, model, ids_to_catch, instance, **kws):
        if instance.pk in ids_to_catch:
            instance._track_changes = child_m._track_changes
            instance._save_with = child_m._save_with

    m._rel_objs_to_catch = defaultdict(dict)
    m._rel_objs_methods = {}
    # Get the related objects.
    related_objects = m._meta.get_all_related_objects()
    related_versioned = [o for o in related_objects if is_versioned(o.model)]
    # Using related objs, build a dictionary mapping model class -> pks
    for rel_o in related_versioned:
        accessor = rel_o.get_accessor_name()
        if not hasattr(m, accessor):
            continue
        # OneToOneField means a single object.
        if rel_o.field.related.field.__class__ == models.OneToOneField:
            objs = [getattr(m, accessor)]
        else:
            objs = getattr(m, accessor).all()
        for o in objs:
            # We use a dictionary for fast lookup in
            # _set_arguments_for
            m._rel_objs_to_catch[o.__class__][o.pk] = True

    # Construct a method that will check to see if the sender is
    # one of the related objects
    for model in m._rel_objs_to_catch:
        ids_to_catch = m._rel_objs_to_catch[model]
        _pass_on_arguments = partial(_set_arguments_for, m, model,
            ids_to_catch)
        models.signals.pre_delete.connect(_pass_on_arguments, sender=model,
            weak=False)
        # Save the method so we can disconnect it
        m._rel_objs_methods[model] = _pass_on_arguments


def save_func(model_save):
    def save(m, *args, **kws):
        return save_with_arguments(model_save, m, *args, **kws)
    return save


def save_with_arguments(model_save, m, force_insert=False, force_update=False,
                        using=None, track_changes=True, **kws):
    """
    A simple custom save() method on models with changes tracked.

    NOTE: All essential logic should go into our post/pre-delete/save
          signal handlers, NOT in this method. Custom delete()
          methods aren't called when doing bulk QuerySet.delete().
    """
    m._track_changes = track_changes
    if not hasattr(m, '_save_with'):
        m._save_with = {}
    m._save_with.update(kws)

    return model_save(m, force_insert=force_insert,
                                      force_update=force_update,
                                      using=using,
    )


def delete_func(model_delete):
    def delete(*args, **kws):
        return delete_with_arguments(model_delete, *args, **kws)
    return delete


def delete_with_arguments(model_delete, m, using=None,
                          track_changes=True, **kws):
    """
    A simple custom delete() method on models with changes tracked.

    NOTE: Most history logic should go into our post/pre-delete/save
          signal handlers, NOT in this method. Custom delete()
          methods aren't called when doing bulk QuerySet.delete().
    """
    m._track_changes = track_changes
    m._save_with = kws

    if is_pk_recycle_a_problem(m):
        m._track_changes = False

    _related_objs_delete_passalong(m)
    return model_delete(m, using=using)
