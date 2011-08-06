from utils import is_versioned


def register(cls, manager_name='versions'):
    """
    Registers the model class `cls` as a versioned model.  After
    registration (and a call to syncdb) changes to the model will be
    tracked.

    Attrs:
        cls: The class to be versioned
        manager_name: Optional name of the manager that's added to cls
            and instances of cls. This is set to 'versions' by default.
    """
    from models import TrackChanges

    if is_versioned(cls):
        return

    t = TrackChanges()
    t.manager_name = manager_name
    t.connect_to(cls)


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
