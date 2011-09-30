from django.http import HttpResponseRedirect

from pages.models import slugify

from models import Redirect


def _is_redirect(response):
    return 'redirected_from' in response.GET


def _force_show_page(response):
    return 'force_show' in response.GET


class RedirectFallbackMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            # No need to check for a redirect for non-404 responses.
            return response
        if _is_redirect(request) or _force_show_page(request):
            # Don't double-redirect and allow the page to be
            # force-displayed.
            return response

        r = None
        # Skip leading slash.
        slug = slugify(request.get_full_path()[1:])
        # Skip trailing slash.
        if slug.endswith('/'):
            slug = slug[:-1]
        try:
            r = Redirect.objects.get(source=slug)
        except Redirect.DoesNotExist:
            pass
        if r is not None:
            return HttpResponseRedirect(
                r.destination.get_absolute_url() +
                '?&redirected_from=%s' % slug
            )

        # No redirect was found. Return the response.
        return response
