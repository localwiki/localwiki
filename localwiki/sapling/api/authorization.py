from tastypie.authorization import Authorization


class ExtendedDjangoAuthorization(Authorization):
    """
    This is a copy of tastypie.authorization.DjangoAuthorization that allows
    us to specify an arbitrary permission and arbitrary object to check that
    permission against.

    Uses permission checking from ``django.contrib.auth`` to map
    ``POST / PUT / DELETE / PATCH`` to their equivalent Django auth
    permissions.
    """
    # XXX TODO replace this all with something cool from the 'perms' branch
    # when it's merged into tastypie master.

    def is_authorized(self, request, object=None):
        # GET-style methods are always allowed.
        if request.method in ('GET', 'OPTIONS', 'HEAD'):
            return True

        klass = self.resource_meta.object_class

        # If it doesn't look like a model, we can't check permissions.
        if not klass or not getattr(klass, '_meta', None):
            return True

        # User must be logged in to check permissions.
        if not hasattr(request, 'user'):
            return False

        permission_codes = []

        # If we don't recognize the HTTP method, we don't know what
        # permissions to check. Deny.
        if request.method not in self.permission_map:
            return False

        for perm in self.permission_map[request.method]:
            permission_codes.append(perm)

        return request.user.has_perms(permission_codes)

    @property
    def permission_map(self):
        klass = self.resource_meta.object_class
        app_model = (klass._meta.app_label, klass._meta.module_name)
        permission_map = {
            'POST': ['%s.add_%s' % app_model],
            'PUT': ['%s.change_%s' % app_model],
            'DELETE': ['%s.delete_%s' % app_model],
            'PATCH': [
                '%s.add_%s' % app_model,
                '%s.change_%s' % app_model,
                '%s.delete_%s' % app_model],
        }
        return permission_map
