import threading

from django.db.models import signals

from fields import AutoSetField, AutoUserField, AutoIPAddressField

# Ignore auto-tracking of user info on these HTTP methods
IGNORE_USER_INFO_METHODS = (
    'GET', 'HEAD', 'OPTIONS', 'TRACE'
)

# NOTE: Thread-local is usually a bad idea.  However, in this case
# it is the most elegant way for us to store per-request data
# and retrieve it from somewhere else.  Our goal is to allow people
# to auto-update fields on a model when it's saved.  By design,
# we have to do something like this.  Signals can be processed by
# different threads, too.
_threadlocal = threading.local()


class AutoTrackUserInfoMiddleware(object):
    """
    Optional middleware to automatically add the current request user's
    information into the historical model as it's saved.
    """
    # If we wanted to track more than ip, user then we could use a
    # passed-in callable for logic.
    def process_request(self, request):
        if request.method in IGNORE_USER_INFO_METHODS:
            pass

        _threadlocal.request = request
        signals.pre_save.connect(self.update_fields, weak=False)

    def _lookup_field_value(self, field):
        request = _threadlocal.request
        if isinstance(field, AutoUserField):
            if hasattr(request, 'user') and request.user.is_authenticated():
                return request.user
        elif isinstance(field, AutoIPAddressField):
            return request.META.get('REMOTE_ADDR', None)

    def update_fields(self, sender, instance, **kws):
        for field in instance._meta.fields:
            # Find our automatically-set-fields.
            if isinstance(field, AutoSetField):
                # only set the field if it's currently empty
                if getattr(instance, field.attname) is None:
                    val = self._lookup_field_value(field)
                    setattr(instance, field.name, val)
