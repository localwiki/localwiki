from models import RecentChanges


class Registry(object):
    def __init__(self):
        self._registry = {}

    def register(self, changes_class):
        self._registry[changes_class] = True

    def get_changes_classes(self):
        return self._registry.keys()

changes_registry = Registry()


def register(changes_class):
    """
    Register a RecentChanges subclass to appear on the Recent Changes page.

    Args:
        changes_class: A subclass of RecentChanges.
    """
    changes_registry.register(changes_class)


def get_changes_classes():
    """
    Returns:
        A list of the registered changes classes.
    """
    return changes_registry.get_changes_classes()
