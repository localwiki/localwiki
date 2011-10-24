import threading

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


class FieldRegistry(threading.local):
    """
    Nailed-to-thread tracking.
    """
    # NOTE: Thread-local is usually a bad idea.  However, in this case
    # it is the most elegant way for us to store per-request data
    # and retrieve it from somewhere else.  Our goal is to allow people
    # to auto-update fields on a model when it's saved.  By design,
    # we have to do something like this.
    _registry = {}

    def __init__(self, type):
        self.type = type
        self._registry.setdefault(self.type, {})

    def add_field(self, model, field):
        reg = self._registry[self.type].setdefault(model, [])
        reg.append(field)

    def get_fields(self, model):
        return self._registry[self.type].get(model, [])

    def __contains__(self, model):
        return model in self._registry[self.type]
