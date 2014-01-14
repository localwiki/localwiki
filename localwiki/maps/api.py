from rest_framework import viewsets
from rest_framework_filters import filters, FilterSet

from main.api import router
from main.api.filters import HistoricalFilter

from regions.api import RegionFilter
from pages.api import PageFilter

from .models import MapData
from .serializers import MapDataSerializer, HistoricalMapDataSerializer


class MapFilter(FilterSet):
    length = filters.AllLookupsFilter(name='length')
    page = filters.RelatedFilter(PageFilter, name='page')
    region = filters.RelatedFilter(RegionFilter, name='region')

    class Meta:
        model = MapData


class HistoricalMapFilter(MapFilter, HistoricalFilter):
    class Meta:
        model = MapData.versions.model


class MapDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows maps to be viewed and edited.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `length` -- Filter by length. Supports the [standard lookup types](../../api_docs/filters)
      * `page` -- Filter by page.  Allows for chained filtering on all of the filters available on the [page resource](../pages/), e.g. `page__slug`.
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.
    """
    queryset = MapData.objects.all()
    serializer_class = MapDataSerializer
    filter_class = MapFilter


class HistoricalMapDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows map history to be viewed.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `length` -- Filter by length. Supports the [standard lookup types](../../api_docs/filters)
      * `page` -- Filter by page.  Allows for chained filtering on all of the filters available on the [page resource](../pages/), e.g. `page__slug`.
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.

    And the usual set of historical filter fields:

      * `history_user` - filter by the `user` resource of the editor, if user was logged in.  Allows for chained filtering on all of the filters available on the [user resource](../users/), e.g. `history_user__username`.
      * `history_user_ip` - filter by the IP address of the editor.
      * `history_date` - filter by history date. Supports the [standard lookup types](../../api_docs/filters)
      * `history_type` - filter by [history type id](../../api_docs/history_type), exact.
    """
    queryset = MapData.versions.all()
    serializer_class = HistoricalMapDataSerializer
    filter_class = HistoricalMapFilter


router.register(u'maps', MapDataViewSet)
router.register(u'maps_history', HistoricalMapDataViewSet)
