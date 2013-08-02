import re

from django.http import HttpResponseRedirect

from pages.models import slugify
from regions.models import Region

from models import Redirect


def _is_redirect(response):
    return 'redirected_from' in response.GET


def _force_show_page(response):
    return 'show' in response.GET


page_routing_pattern = re.compile(
    '^/(?P<region>[^/]+?)/(?P<slug>.+)/*'
)

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

        re_match = page_routing_pattern.match(request.get_full_path())
        slug = slugify(re_match.group('slug'))
        region_slug = re_match.group('region')
        region = Region.objects.get(slug=region_slug)

        try:
            r = Redirect.objects.get(source=slug, region=region)
        except Redirect.DoesNotExist:
            pass
        if r is not None:
            return HttpResponseRedirect(
                r.destination.get_absolute_url() +
                '?&redirected_from=%s' % slug
            )

        # No redirect was found. Return the response.
        return response
