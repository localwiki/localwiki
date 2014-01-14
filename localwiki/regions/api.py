from django.conf import settings

from rest_framework import viewsets
from rest_framework_filters import filters, FilterSet

from main.api import router

from .models import Region, RegionSettings
from .serializers import RegionSerializer


class RegionSettingsFilter(FilterSet):
    class Meta:
        model = RegionSettings
        fields = ('default_language',)


class RegionFilter(FilterSet):
    slug = filters.AllLookupsFilter(name='slug')
    settings = filters.RelatedFilter(RegionSettingsFilter, name='regionsettings')

    class Meta:
        model = Region
        fields = ('slug',)


allowed_languages = ''
for l in settings.LANGUAGES[:-1]:
    allowed_languages += '`%s`, ' % l[0]
allowed_languages += '`%s`' % settings.LANGUAGES[-1][0]

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    __doc__ = """
    API endpoint that allows regions to be viewed.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `slug` -- Filter by region slug. Supports the [standard lookup types](../../api_docs/filters)
      * `settings`
        * `settings__default_language` -- Filter by the region's default language.  Accepts one of %(allowed_languages)s.
    """ % {'allowed_languages': allowed_languages}

    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_class = RegionFilter


router.register(u'regions', RegionViewSet)
