class FieldRegistry(object):
    """
    Simple nailed-to-class tracking.
    """
    _registry = {}

    def __init__(self, type):
        self.type = type
        self.__class__._registry.setdefault(self.type, {})

    def add_field(self, model, field):
        reg = self.__class__._registry[self.type].setdefault(model, [])
        reg.append(field)

    def get_fields(self, model):
        return self.__class__._registry[self.type].get(model, [])

    def __contains__(self, model):
        return model in self.__class__._registry[self.type]
