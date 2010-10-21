class HistoricalObjectDescriptor(object):
    def __init__(self, model):
        self.model = model

    def __get__(self, instance, owner):
        values = (getattr(instance, f.attname) for f in self.model._meta.fields)
        return self.model(*values)

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

def revert_to(hm, delete_newer_versions=False):
    """
    This is used on a *historical instance* - e.g. something you get
    using history.get(..) rather than an instance of the model.  Like:

    ph = p.history.as_of(..)
    ph.revert_to()

    Reverts to this version of the model.

    @param delete_newer_versions: if True, delete all versions in the
           history newer than this version.
    """
    # the original model instance
    m = hm.history_info.object
    if delete_newer_versions:
        newer = m.history.filter(date__gt=hm.history_info.date)
        for v in newer:
            v.delete()
    m.save()

def no_attribute_setting(o, x):
    raise TypeError("You can't set this attribute!")

def version_number_of(hm):
    """
    Returns version number.

    @param hm: history object.
    """
    if getattr(hm.history_info.instance, '_version_number', None) is None:
        date = hm.history_info.date
        obj = hm.history_info.object
        hm.history_info.instance._version_number = len(
            obj.history.filter(history_date__lte=date)
        )
    return hm.history_info.instance._version_number
