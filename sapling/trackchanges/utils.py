from functools import partial

from django.utils.functional import SimpleLazyObject
from django.db import models

from constants import *

def save_with_arguments(m, force_insert=False, force_update=False, using=None,
                        track_changes=True, **kws):
    m._track_changes = track_changes
    m._save_with = kws
    return super(m.__class__, m).save(force_insert=force_insert,
                                      force_update=force_update,
                                      using=using,
    )

def delete_with_arguments(m, using=None, track_changes=True, **kws):
    m._track_changes = track_changes
    m._save_with = kws
    return super(m.__class__, m).delete(using=using)

class HistoricalObjectDescriptor(object):
    def __init__(self, model):
        self.model = model

    def __get__(self, instance, owner):
        values = (getattr(instance, f.attname) for f in self.model._meta.fields)
        m = self.model(*values)
        return m

def _wrapped_getattribute(m, name):
    print "IN WRAPPED GETATTRIBUTE"
    direct_val = m._direct_lookup_fields.get(name, None)
    if direct_val is not None:
        return direct_val
    return m.__base_getattribute(m, name)

def _wrap_foreign_keys(m):
    """
    Sets the foriegn key fields to the historical versions of the
    foreign keys if the related objects are versioned.

    Wraps these in SimpleLazyObjects so the lookup doesn't happen unless
    the objects are used.

    @param m: a historical record model
    """
    def _lookup_version(m, fk_obj):
        history_manager = getattr(fk_obj, fk_obj._history_manager_name)
        print "looking up as of..", m.history_info.date
        return history_manager.as_of(date=m.history_info.date)

    def _wrap_field(m, field):
        fk_obj = getattr(m, field.name)
        # if we have this attribute then the object is versioned
        if hasattr(fk_obj, '_history_manager_name'):
            print "HAS ATTR OF HISTORY MANAGER"
            _lookup_proper_fk_version = partial(_lookup_version, m, fk_obj)
            print "SET", field.name, "to lookup old fk version on", m
            m._direct_lookup_fields[field.name] = SimpleLazyObject(
                _lookup_proper_fk_version
            )

    m._direct_lookup_fields = {}
    for field in m.history_info._object._meta.fields:
        if isinstance(field, models.ForeignKey):
            _wrap_field(m, field)
    for field in m._meta.many_to_many:
        _wrap_field(m, field)

def historical_record_getattribute(model, m, name):
    """
    We have to define our own __getattribute__ because otherwise there's
    no way to set our wrapped foreign key attributes.
    
    If we try and set
    history_instance.att = SimpleLazyObject(_lookup_proper_fk_version)
    we'll get an error because Django does an isinstance() check on
    assignment to model fields.  Additionally, the __set__ method on
    related fields will force evaluation due to equality checks.
    """
    basedict = model.__getattribute__(m, '__dict__')
    direct_val = basedict.get('_direct_lookup_fields', {}).get(name)
    if direct_val is not None:
        return direct_val
    return model.__getattribute__(m, name)

def historical_record_init(m, *args, **kws):
    """
    This is the __init__ method of historical record instances.
    """
    retval = super(m.__class__, m).__init__(*args, **kws)
    _wrap_foreign_keys(m)
    return retval

#########################################################
#
#  Methods that act on historical record instances
#
#########################################################

class HistoricalMetaInfo(object):
    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def __getattr__(self, name):
        try:
            return getattr(self.__dict__['instance'], 'history_%s' % name)
        except AttributeError, s:
            raise AttributeError("history_info has no attribute %s" % name)

    def __setattr__(self, name, val):
        if name == 'instance':
            self.__dict__['instance'] = val
            return
        try:
            self.__dict__['instance'].__setattr__('history_%s' % name, val)
        except AttributeError, s:
            raise AttributeError("history_info has no attribute %s" % name)

def revert_to(hm, delete_newer_versions=False, **kws):
    """
    This is used on a *historical instance* - e.g. something you get
    using history.get(..) rather than an instance of the model.  Like:

    ph = p.history.as_of(..)
    ph.revert_to()

    Reverts to this version of the model.

    @param delete_newer_versions: if True, delete all versions in the
             history newer than this version.
    @param track_changes: if False, won't log *this revert* as an action in
             the history log.
    """
    m = hm.history_info._object

    # If we simply grab hm.history_info._object we may hit a uniqueness exception
    # if we save the model and it already exists.  This is because the pk of the
    # model may have changed if it was deleted at some time.

    # get the current model instance if it exists
    unique_fields = unique_fields_of(m)
    if unique_fields:
        ms = m.__class__.objects.filter(**unique_fields)
        if ms:
            # keep the primary key unique
            m.pk = ms[0].pk

    if delete_newer_versions:
        newer = m.history.filter(history_info__date__gt=hm.history_info.date)
        for v in newer:
            v.delete(track_changes=False)
    m._history_type = TYPE_REVERTED
    if hm.history_info.type == TYPE_DELETED:
        # We are reverting to a deleted version of the model
        # so..delete the model!
        m.delete(reverted_to_version=hm)
    else:
        m.save(reverted_to_version=hm, **kws)

def no_attribute_setting(o, x):
    raise TypeError("You can't set this attribute!")

def version_number_of(hm):
    """
    Returns version number.

    @param hm: history object.
    """
    if getattr(hm.history_info.instance, '_version_number', None) is None:
        date = hm.history_info.date
        obj = hm.history_info._object
        hm.history_info.instance._version_number = len(
            obj.history.filter(history_date__lte=date)
        )
    return hm.history_info.instance._version_number

def unique_fields_of(m):
    """
    Returns a name: value dictionary of the unique fields of the
    model instance m.

    @param m: An instance of a model.
    """
    for field in m._meta.fields:
        if field.primary_key or field.auto_created: continue
        if not field.unique: continue

        # related objects have attname set to something_id for some reason
        if hasattr(field, 'related'):
            return { field.name: getattr(m, field.name) }
        return { field.attname: getattr(m, field.attname) }

    if m._meta.unique_together:
        unique_fields = {}
        # tuple of field names, e.g. ('email', 'cellphone')
        for k in m._meta.unique_together[0]:
            unique_fields[k] = getattr(m, k)
        return unique_fields
