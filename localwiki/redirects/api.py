from rest_framework import viewsets
from rest_framework_filters import filters, FilterSet

from main.api import router
from main.api.filters import HistoricalFilter
from pages.api import PageFilter
from regions.api import RegionFilter

from .models import Redirect
from .serializers import RedirectSerializer, HistoricalRedirectSerializer


class RedirectFilter(FilterSet):
    source = filters.AllLookupsFilter(name='source')
    destination = filters.RelatedFilter(PageFilter, name='destination')
    region = filters.RelatedFilter(RegionFilter, name='region')

    class Meta:
        model = Redirect


class HistoricalRedirectFilter(RedirectFilter, HistoricalFilter):
    class Meta:
        model = Redirect.versions.model


class RedirectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows redirects to be viewed and edited.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `source` -- Filter by source slug. Supports the [standard lookup types](../../api_docs/filters)
      * `destination` -- Filter by destination page.  Allows for chained filtering on all of the filters available on the [page resource](../pages/), e.g. `destination__slug`.
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.
    """
    queryset = Redirect.objects.all()
    serializer_class = RedirectSerializer
    filter_class = RedirectFilter


class HistoricalRedirectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows redirect history to be viewed.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `source` -- Filter by source slug. Supports the [standard lookup types](../../api_docs/filters)
      * `destination` -- Filter by destination page.  Allows for chained filtering on all of the filters available on the [page resource](../pages/), e.g. `destination__slug`.
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.

    And the usual set of historical filter fields:

      * `history_user` - filter by the `user` resource of the editor, if user was logged in.  Allows for chained filtering on all of the filters available on the [user resource](../users/), e.g. `history_user__username`.
      * `history_user_ip` - filter by the IP address of the editor.
      * `history_date` - filter by history date. Supports the [standard lookup types](../../api_docs/filters)
      * `history_type` - filter by [history type id](../../api_docs/history_type), exact.
    """
    queryset = Redirect.versions.all()
    serializer_class = HistoricalRedirectSerializer
    filter_class = HistoricalRedirectFilter


router.register(u'redirects', RedirectViewSet)
router.register(u'redirects_history', HistoricalRedirectViewSet)
