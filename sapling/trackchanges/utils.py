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
