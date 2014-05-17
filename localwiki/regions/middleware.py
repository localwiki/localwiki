import re

from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from django.utils.http import urlquote

from models import Region

region_routing_pattern = re.compile(
    '^/(?P<region>[^/]+?)(/(?P<rest>.*))?$'
)

LANGUAGES = [i[0] for i in settings.LANGUAGES]


class RedirectToLanguageSubdomainMiddleware(object):
    """
    Redirect to the language-specific subdomain associated with this
    region, if the region has a language set that's not the default
    (global) language.
    """
    def process_request(self, request):
        re_match = region_routing_pattern.match(request.get_full_path())
        if not re_match:
            return

        region_slug = re_match.group('region')
        rs = Region.objects.filter(slug=region_slug)
        if not rs:
            return
        region = rs[0]

        if not hasattr(region, 'regionsettings'):
            region_lang = settings.LANGUAGE_CODE
        else:
            region_lang = region.regionsettings.default_language or settings.LANGUAGE_CODE
        request_lang = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)

        # If the region has the same language as indicated by the subdomain (request lang),
        # keep them on the same domain.
        if request_lang == region_lang:
            return

        host = request.get_host().split('.')

        # We keep the language code in the subdomain, unless we're on the default language.
        if request_lang == settings.LANGUAGE_CODE:
            base_hostname = '.'.join(host)
        else:
            base_hostname = '.'.join(host[1:])

        # Send them to the subdomain appropriate for the language
        if region_lang == settings.LANGUAGE_CODE:
            domain = base_hostname
        else:
            domain = '%s.%s' % (region_lang, base_hostname)

        uri = '%s://%s%s%s' % (
            request.is_secure() and 'https' or 'http',
            domain,
            urlquote(request.path),
            (request.method == 'GET' and len(request.GET) > 0) and '?%s' % request.GET.urlencode() or ''
        )
        return HttpResponsePermanentRedirect(uri)
