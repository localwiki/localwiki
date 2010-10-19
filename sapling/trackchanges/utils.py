class HistoricalObjectDescriptor(object):
    def __init__(self, model):
        self.model = model

    def __get__(self, instance, owner):
        values = (getattr(instance, f.attname) for f in self.model._meta.fields)
        return self.model(*values)

class HistoricalMetaInfo(object):
    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def __getattr__(self, name):
        try:
            return getattr(self.__dict__['instance'], 'history_%s' % name)
        except AttributeError, s:
            raise AttributeError("history_meta has no attribute %s" % name)

def version_number_of(v):
    """
    Returns version number.

    @param v: history object.
    """
    if getattr(v.history_meta.instance, '_version_number', None) is None:
        date = v.history_meta.date
        obj = v.history_meta.object
        v.history_meta.instance._version_number = len(
            obj.history.filter(history_date__lte=date)
        )
    return v.history_meta.instance._version_number
