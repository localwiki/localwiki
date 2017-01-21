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

        user = None
        if hasattr(request, 'user') and request.user.is_authenticated():
            user = request.user
        ip = request.META.get('REMOTE_ADDR', None)
        self._set_lookup_fields(user=user, ip=ip)

        signals.pre_save.connect(self.update_fields, weak=False)

    def _set_lookup_fields(self, **kws):
        for k, v in kws.iteritems():
            setattr(_threadlocal, '_userinfo_%s' % k, v)

    def _lookup_field_value(self, field):
        if isinstance(field, AutoUserField):
            field_type = 'user'
        elif isinstance(field, AutoIPAddressField):
            field_type = 'ip'

        return getattr(_threadlocal, '_userinfo_%s' % field_type)

    def update_fields(self, sender, instance, **kws):
        for field in instance._meta.fields:
            # Find our automatically-set-fields.
            if isinstance(field, AutoSetField):
                # only set the field if it's currently empty
                if getattr(instance, field.attname) is None:
                    val = self._lookup_field_value(field)
                    setattr(instance, field.name, val)
