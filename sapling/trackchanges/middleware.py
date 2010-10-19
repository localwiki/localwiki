import functools
from django.db.models import signals

from registry import FieldRegistry

"""
Right now this just interacts with the AutoUserField
should be made to also work with like AutoIPAddressField
"""

# Ignore auto-tracking of user info on these HTTP methods
IGNORE_USER_INFO_METHODS = (
    'GET', 'HEAD', 'OPTIONS', 'TRACE'
)

class AutoTrackUserInfoMiddleware(object):
    def process_request(self, request):
        if request.method in IGNORE_USER_INFO_METHODS:
            pass

        user = None
        if hasattr(request, 'user') and request.user.is_authenticated():
            user = request.user

        update_users = functools.partial(self.update_users, user)
        signals.pre_save.connect(update_users, dispatch_uid=request, weak=False)

    def update_users(self, user, sender, instance, **kws):
        registry = FieldRegistry()
        if sender in registry:
            for field in registry.get_fields(sender):
                # only set the field if it's currently empty
                if getattr(instance, field.name) is None:
                    setattr(instance, field.name, user)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid=request)
        return response
