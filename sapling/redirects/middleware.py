from django.http import HttpResponsePermanentRedirect

from pages.models import slugify

from models import Redirect


class RedirectFallbackMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            # No need to check for a redirect for non-404 responses.
            return response
        r = None
        # Skip leading slash.
        slug = slugify(request.get_full_path()[1:])
        try:
            r = Redirect.objects.get(source=slug)
        except Redirect.DoesNotExist:
            pass
        # Try removing the trailing slash, if it exists.
        if r is None and slug.endswith('/'):
            try:
                r = Redirect.objects.get(source=slug[:-1])
            except Redirect.DoesNotExist:
                pass
        if r is not None:
            return HttpResponsePermanentRedirect(r.destination.get_absolute_url())

        # No redirect was found. Return the response.
        return response
