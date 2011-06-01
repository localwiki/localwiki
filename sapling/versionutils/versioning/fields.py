from django.db import models
from django.contrib.auth.models import User

from registry import *


class AutoUserField(models.ForeignKey):
    def __init__(self, **kws):
        super(AutoUserField, self).__init__(User, **kws)

    def contribute_to_class(self, cls, name):
        super(AutoUserField, self).contribute_to_class(cls, name)
        registry = FieldRegistry('user')
        registry.add_field(cls, self)


class AutoIPAddressField(models.IPAddressField):
    def contribute_to_class(self, cls, name):
        super(AutoIPAddressField, self).contribute_to_class(cls, name)
        registry = FieldRegistry('ip')
        registry.add_field(cls, self)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^versionutils\.versioning\.fields"])
except ImportError:
    pass
