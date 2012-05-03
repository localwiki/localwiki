from django.middleware.cache import UpdateCacheMiddleware

from django.utils.cache import learn_cache_key, get_max_age


class UpdateCacheMiddlewareNoHeaders(UpdateCacheMiddleware):
    """
    Just like UpdateCacheMiddleware but we don't set cache headers in the
    HTTP response.
    """
    def process_response(self, request, response):
        """Sets the cache, if needed."""
        if not self._should_update_cache(request, response):
            # We don't need to update the cache, just return.
            return response
        if not response.status_code == 200:
            return response
        # Try to get the timeout from the "max-age" section of the "Cache-
        # Control" header before reverting to using the default cache_timeout
        # length.
        timeout = get_max_age(response)
        if timeout == None:
            timeout = self.cache_timeout
        elif timeout == 0:
            # max-age was set to 0, don't bother caching.
            return response
        #patch_response_headers(response, timeout)
        if timeout:
            cache_key = learn_cache_key(
                request, response, timeout, self.key_prefix, cache=self.cache)
            if hasattr(response, 'render') and callable(response.render):
                response.add_post_render_callback(
                    lambda r: self.cache.set(cache_key, r, timeout)
                )
            else:
                self.cache.set(cache_key, response, timeout)
        return response


class UpdateCacheMiddlewareNoEdit(UpdateCacheMiddleware):
    """
    Just like UpdateCacheMiddleware but don't cache anything from anyone
    who has the 'has_POSTed' session flag.  We use this because the default
    CACHE_MIDDLEWARE_ANONYMOUS_ONLY will still cache non-logged in users'
    edits, etc.  So we sort of say that 'anonymous,' in our case, is really
    anyone who's never made an edit.
    """
    def _should_update_cache(self, request, response):
        if (not hasattr(request, '_cache_update_cache') or
            not request._cache_update_cache):
            return False
        # If the session has not been accessed otherwise, we don't want to
        # cause it to be accessed here. If it hasn't been accessed, then the
        # user's logged-in status has not affected the response anyway.
        if self.cache_anonymous_only and self._session_accessed(request):
            assert hasattr(request, 'user'), "The Django cache middleware with CACHE_MIDDLEWARE_ANONYMOUS_ONLY=True requires authentication middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware' before the CacheMiddleware."
            if request.user.is_authenticated() or request.session.get('has_POSTed'):
                # Don't cache user-variable requests from authenticated users.
                return False
        return True


class UpdateCacheMiddleware(UpdateCacheMiddlewareNoEdit, UpdateCacheMiddlewareNoHeaders):
    pass


class TrackPOSTMiddleware(object):
    def process_request(self, request):
        if request.method == 'POST' and 'has_POSTed' not in request.session:
            request.session['has_POSTed'] = True
