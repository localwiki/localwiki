from tastypie.authentication import (MultiAuthentication, Authentication,
    ApiKeyAuthentication)


class ApiKeyWriteAuthentication(MultiAuthentication):
    """
    We allow anyone, whether using an API key or not, to read, but you can
    only write when using an API key.
    """
    def __init__(self, **kwargs):
        return super(ApiKeyWriteAuthentication, self).__init__(
            ApiKeyAuthentication(), Authentication(), **kwargs)

    def is_authenticated(self, request, **kwargs):
        """
        Identifies if the user is authenticated to continue or not.

        Should return either ``True`` if allowed, ``False`` if not or an
        ``HttpResponse`` if you need something custom.
        """
        authenticated = super(ApiKeyWriteAuthentication,
            self).is_authenticated(request, **kwargs)

        if request.method == 'GET':
            return authenticated

        # Only allow API key requests to do writing
        if isinstance(request._authentication_backend, ApiKeyAuthentication):
            return authenticated

        return False
