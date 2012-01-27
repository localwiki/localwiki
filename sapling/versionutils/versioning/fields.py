from django.db import models
from django.contrib.auth.models import User


class AutoSetField(object):
    pass


class AutoUserField(models.ForeignKey, AutoSetField):
    def __init__(self, **kws):
        if 'to' in kws:
            # Fixes south.  We always want this to point to the User
            # model.
            del kws['to']
        return super(AutoUserField, self).__init__(User, **kws)


class AutoIPAddressField(models.IPAddressField, AutoSetField):
    pass

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^versionutils\.versioning\.fields"])
except ImportError:
    pass
