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
