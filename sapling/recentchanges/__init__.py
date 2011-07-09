from models import RecentChanges


class Registry(object):
    def __init__(self):
        self._registry = []

    def register(self, changes_class):
        self._registry.append(changes_class)

    def get_changes_classes(self):
        return self._registry

changes_registry = Registry()


def register(changes_class):
    changes_registry.register(changes_class)


def get_changes_classes():
    return changes_registry.get_changes_classes()
