from django.contrib.sites.models import Site
from django.conf import settings

from tastypie.resources import ModelResource

from sapling.api import api


class SiteResource(ModelResource):
    class Meta:
        # For now, let's just show the default site.
        queryset = Site.objects.filter(id=settings.SITE_ID)

    def dehydrate(self, bundle):
        bundle.data['license'] = settings.GLOBAL_LICENSE_NOTE
        bundle.data['signup_tos'] = settings.SIGNUP_TOS
        bundle.data['time_zone'] = settings.TIME_ZONE
        bundle.data['language_code'] = settings.LANGUAGE_CODE
        return bundle


api.register(SiteResource())
