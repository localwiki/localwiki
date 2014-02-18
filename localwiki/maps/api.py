from rest_framework import viewsets
from rest_framework_filters import filters, FilterSet
from rest_framework_gis.filters import GeoFilterSet

from main.api import router
from main.api.filters import HistoricalFilter
from main.api.views import AllowFieldLimitingMixin
from regions.api import RegionFilter
from pages.api import PageFilter, PagePermissionsMixin

from .models import MapData
from .serializers import MapDataSerializer, HistoricalMapDataSerializer


class MapFilter(GeoFilterSet, FilterSet):
    points = filters.AllLookupsFilter(name='points')
    lines = filters.AllLookupsFilter(name='lines')
    polys = filters.AllLookupsFilter(name='polys')
    page = filters.RelatedFilter(PageFilter, name='page')
    region = filters.RelatedFilter(RegionFilter, name='region')
    length = filters.AllLookupsFilter(name='length')

    class Meta:
        model = MapData


class HistoricalMapFilter(HistoricalFilter, MapFilter):
    polys = filters.AllLookupsFilter(name='polys')

    class Meta:
        model = MapData.versions.model


class MapDataViewSet(PagePermissionsMixin, AllowFieldLimitingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows maps to be viewed and edited.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `points` -- Filter by the points, if present.  Supports the [standard geographic lookup types](http://localwiki.net/main/API_Documentation#geo_lookups)
      * `lines` -- Filter by the lines, if present.  Supports the [standard geographic lookup types](http://localwiki.net/main/API_Documentation#geo_lookups)
      * `polys` -- Filter by the polygons, if present.  Supports the [standard geographic lookup types](http://localwiki.net/main/API_Documentation#geo_lookups)
      * `page` -- Filter by page.  Allows for chained filtering on all of the filters available on the [page resource](../pages/), e.g. `page__slug`.
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.
      * `length` -- Filter by length of the geography. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)

    Ordering
    --------

    You can order the result set by providing the `ordering` query parameter with the value of one of:

      * `length`

    You can reverse ordering by using the `-` sign, e.g. `-length`.
    """
    queryset = MapData.objects.all()
    serializer_class = MapDataSerializer
    filter_class = MapFilter
    ordering_fields = ('length',)


class HistoricalMapDataViewSet(AllowFieldLimitingMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows map history to be viewed.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `points` -- Filter by the points, if present.  Supports the [standard geographic lookup types](http://localwiki.net/main/API_Documentation#geo_lookups)
      * `lines` -- Filter by the lines, if present.  Supports the [standard geographic lookup types](http://localwiki.net/main/API_Documentation#geo_lookups)
      * `polys` -- Filter by the polygons, if present.  Supports the [standard geographic lookup types](http://localwiki.net/main/API_Documentation#geo_lookups)
      * `page` -- Filter by page.  Allows for chained filtering on all of the filters available on the [page resource](../pages/), e.g. `page__slug`.
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.
      * `length` -- Filter by length of the geography. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)

    And the usual set of historical filter fields:

      * `history_user` - filter by the `user` resource of the editor, if user was logged in.  Allows for chained filtering on all of the filters available on the [user resource](../users/), e.g. `history_user__username`.
      * `history_user_ip` - filter by the IP address of the editor.
      * `history_date` - filter by history date. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `history_type` - filter by [history type id](../../api_docs/history_type), exact.

    Ordering
    --------

    You can order the result set by providing the `ordering` query parameter with the value of one of:

      * `length`
      * `history_date`

    You can reverse ordering by using the `-` sign, e.g. `-length`.
    """
    queryset = MapData.versions.all()
    serializer_class = HistoricalMapDataSerializer
    filter_class = HistoricalMapFilter
    ordering_fields = ('length', 'history_date')


router.register(u'maps', MapDataViewSet)
router.register(u'maps_history', HistoricalMapDataViewSet)
