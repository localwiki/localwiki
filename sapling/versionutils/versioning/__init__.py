from models import TrackChanges


def register(cls, manager_name='versions'):
    """
    Attrs:
        cls: The class to be versioned
        manager_name: Optional name of the manager that's added to cls
            and instances of cls. This is set to 'versions' by default.
    """
    t = TrackChanges()
    t.manager_name = manager_name
    t.connect_to(cls)
