from django.conf import settings

from utils import is_versioned


def register(cls, manager_name='versions', changes_tracker=None):
    """
    Registers the model class `cls` as a versioned model.  After
    registration (and a call to syncdb) changes to the model will be
    tracked.

    Args:
      cls: The class to be versioned.
      manager_name: Optional name of the manager that's added to cls
        instances of cls. This is set to 'versions' by default.
      changes_tracker: An optional instance of ChangesTracker.
    """
    from models import ChangesTracker

    if changes_tracker is None:
        changes_tracker = ChangesTracker

    if is_versioned(cls):
        return

    tracker = changes_tracker()
    tracker.connect(cls, manager_name=manager_name)


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
