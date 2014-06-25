import threading
import time
import re

from django.middleware.cache import UpdateCacheMiddleware
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date
from django.middleware.cache import FetchFromCacheMiddleware as DefaultFetchFromCacheMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import MiddlewareNotUsed
from django.conf import settings
from django.utils.importlib import import_module
from django.utils import translation
from django.utils.cache import learn_cache_key, get_max_age


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


# XXX TODO: Hacky. Kill this when on Varnish, as it's not needed. We will
# simply Vary on the Host header with Varnish and disable the cache middleware.
class UpdateCacheMiddlewareHostHeader(UpdateCacheMiddleware):
    def process_response(self, request, response):
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX + request.META.get('HTTP_HOST', '')
        return super(UpdateCacheMiddlewareHostHeader, self).process_response(request, response)


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


class UpdateCacheMiddleware(UpdateCacheMiddlewareHostHeader, UpdateCacheMiddlewareNoEdit, UpdateCacheMiddlewareNoHeaders):
    pass


class FetchFromCacheMiddleware(DefaultFetchFromCacheMiddleware):
    STRIP_RE = re.compile(r'\b(_[^=]+=.+?(?:; |$))')

    def process_request(self, request):
        # Clear Google Analytics cookies
        cookie = self.STRIP_RE.sub('', request.META.get('HTTP_COOKIE', ''))   
        request.META['HTTP_COOKIE'] = cookie

        if request.user.is_authenticated() or request.session.get('has_POSTed'):
            return False  # Don't cache if they've posted or are authenticated

        # XXX HACK: remove once we're on Varnish.
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX + request.META.get('HTTP_HOST', '')

        return super(FetchFromCacheMiddleware, self).process_request(request)


class TrackPOSTMiddleware(object):
    def process_request(self, request):
        if request.method == 'POST' and 'has_POSTed' not in request.session:
            request.session['has_POSTed'] = True


class SubdomainLanguageMiddleware(object):
    """
    Set the language for the site based on the subdomain the request
    is being served on. For example, serving on 'fr.domain.com' would
    make the language French (fr).
    """
    LANGUAGES = [i[0] for i in settings.LANGUAGES]

    def process_request(self, request):
        host = request.get_host().split('.')
        if host and host[0] in self.LANGUAGES:
            lang = host[0]
        else:
            # Set to default language
            lang = settings.LANGUAGE_CODE
        translation.activate(lang)
        request.LANGUAGE_CODE = lang


class SessionMiddleware(SessionMiddleware):
    """
    A variant of SessionMiddleware that plays nicely with
    non-canonical LocalWiki (rare) custom domain names.
    """
    def process_response(self, request, response):
        session_cookie_domain = settings.SESSION_COOKIE_DOMAIN
        hostname = request.META.get('HTTP_HOST', '').split(':')[0]
        if session_cookie_domain:
            if not hostname.startswith(session_cookie_domain.lstrip('.')):
                # Set to empty to allow the cookie to be set. This means
                # subdomains aren't allowed here.
                session_cookie_domain = ''

        # Copied from SessionMiddleware (can't subclass due to hard-coded settings)
        try:
            accessed = request.session.accessed
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if accessed:
                patch_vary_headers(response, ('Cookie',))
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = cookie_date(expires_time)
                # Save the session data and refresh the client cookie.
                # Skip session save for 500 responses, refs #3881.
                if response.status_code != 500:
                    request.session.save()
                    response.set_cookie(settings.SESSION_COOKIE_NAME,
                            request.session.session_key, max_age=max_age,
                            expires=expires, domain=session_cookie_domain,
                            path=settings.SESSION_COOKIE_PATH,
                            secure=settings.SESSION_COOKIE_SECURE or None,
                            httponly=settings.SESSION_COOKIE_HTTPONLY or None)
        return response


# NOTE: Thread-local is usually a bad idea.  However, in this case
# it is the most elegant way for us to store per-request data
# and retrieve it from somewhere else.  Our goal is to allow a
# signal to have access to the request hostname.  The alternative
# here would be hard-coding the hostname in settings, but this
# is a bit better because we can e.g. detect if we're using
# HTTPS or not.
_threadlocal = threading.local()


class RequestURIMiddleware(object):
    """
    Get and save the current host's base URI.  Contains no trailing slash.
    """
    def process_request(self, request):
        _threadlocal.base_uri = request.build_absolute_uri('/')[:-1]
