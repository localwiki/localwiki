from models import TrackChanges

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
    if is_versioned(cls):
        return

    t = TrackChanges()
    t.manager_name = manager_name
    t.connect_to(cls)
