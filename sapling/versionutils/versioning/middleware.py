import functools
from django.db.models import signals

from registry import FieldRegistry

# Ignore auto-tracking of user info on these HTTP methods
IGNORE_USER_INFO_METHODS = (
    'GET', 'HEAD', 'OPTIONS', 'TRACE'
)


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

        # Disconnect a possibly un-cleaned up prior signal
        signals.pre_save.disconnect(dispatch_uid='update_fields')

        update_fields = functools.partial(self.update_fields, user, ip)
        signals.pre_save.connect(
            update_fields, dispatch_uid='update_fields', weak=False
        )

    def update_fields(self, user, ip, sender, instance, **kws):
        registry = FieldRegistry('user')
        if sender in registry:
            for field in registry.get_fields(sender):
                # only set the field if it's currently empty
                if getattr(instance, field.name) is None:
                    setattr(instance, field.name, user)

        registry = FieldRegistry('ip')
        if sender in registry:
            for field in registry.get_fields(sender):
                # only set the field if it's currently empty
                if getattr(instance, field.name) is None:
                    setattr(instance, field.name, ip)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid='update_fields')
        return response

    def process_exception(self, request, exception):
        signals.pre_save.disconnect(dispatch_uid='update_fields')
