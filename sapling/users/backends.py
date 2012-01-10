from django.contrib.auth.models import User
from guardian.backends import ObjectPermissionBackend
from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from guardian.models import UserObjectPermission, GroupObjectPermission


class CaseInsensitiveModelBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class RestrictiveBackend(object):
    """ Allows restricting permissions on per-object basis.

    For objects, checks object permissions first. If none found checks model
    permissions.  Works pretty much as usual for model permissions.

    NOTE: Make sure this is the only authentication backend providing
    permissions or it won't work, since Django will ask all backends and just
    needs one backend to return True in order to grant the permission.

    If no permissions are found at all, returns the value of the
    USERS_LOGGED_IN_HAS_PERM setting, or False if it's not set.  Set this to
    True if you want to allow everything that is not restricted on a per-object
    level, as long as the user is logged in.  Remember, you can control
    anonymous user permissions separately. See the ANONYMOUS_USER_ID setting
    (from django-guardian) and the USERS_ANONYMOUS_GROUP setting.

    Supports ban list through the optional USERS_BANNED_GROUP setting. Note
    that users in this group will not have ANY permissions, regardless of
    what the group's permissions are set to. It is only a way to indicate which
    users are banned and does not behave like a regular group when it comes
    to permissions.

    Uses django-guardian internally to check object permissions and the default
    django.contrib.auth.backends.ModelBackend for model permissions.
    """
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True
    _object_backend = ObjectPermissionBackend()
    _model_backend = ModelBackend()

    def authenticate(self, username=None, password=None):
        return None

    def is_banned(self, user_obj):
        return (BANNED_GROUP and
               user_obj.groups.filter(name=BANNED_GROUP).exists())

    def has_perm(self, user_obj, perm, obj=None):
        default_has_perm = False
        if user_obj.is_authenticated():
            default_has_perm = LOGGED_IN_HAS_PERM
        else:
            user_obj = User.objects.get(pk=ANONYMOUS_USER_ID)
        if not user_obj.is_active:
            return False
        if user_obj.is_superuser:
            return True
        if self.is_banned(user_obj):
            return False
        if obj and self.object_has_perms(obj):
            return self._object_backend.has_perm(user_obj, perm, obj)
        has_model_perm = self._model_backend.has_perm(user_obj, perm)
        return has_model_perm or default_has_perm

    def object_has_perms(self, obj):
        return (GroupObjectPermission.objects.filter(object_pk=obj.pk).exists()
                or
                UserObjectPermission.objects.filter(object_pk=obj.pk).exists())

ANONYMOUS_USER_ID = settings.ANONYMOUS_USER_ID  # we *want* error if not set
BANNED_GROUP = getattr(settings, "USERS_BANNED_GROUP", None)
LOGGED_IN_HAS_PERM = getattr(settings, "USERS_LOGGED_IN_HAS_PERM", False)
