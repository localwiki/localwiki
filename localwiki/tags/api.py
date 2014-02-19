from rest_framework import viewsets
from rest_framework_filters import FilterSet, filters
from rest_framework_gis.filters import GeoFilterSet

from main.api import router
from main.api.filters import HistoricalFilter
from main.api.views import AllowFieldLimitingMixin

from .models import Tag, PageTagSet, slugify

from .serializers import HistoricalPageTagSetSerializer


class TagFilter(filters.Filter):
    def filter(self, qs, value):
        value = value.strip()
        if not value:
            return qs
        for v in value.split(','):
            qs = qs.filter(tags__slug=v)
        return qs


class HistoricalTagFilter(GeoFilterSet, HistoricalFilter):
    tags = TagFilter()

    class Meta:
        model = PageTagSet.versions.model


class HistoricalTagViewSet(AllowFieldLimitingMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing tag history, grouped by tags on a particular page at a particular point in time.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `tags` -- Filter by tag.  E.g. `tags=park` for all historical tag sets containing 'park', or `tags=park,wifi` for all historical tag sets containing 'park' **and** also tagged 'wifi'.
      * `page` -- Filter by page.  Allows for chained filtering on all of the filters available on the [page resource](../pages/), e.g. `page__slug`.
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.

    And the usual set of historical filter fields:

      * `history_user` - filter by the `user` resource of the editor, if user was logged in.  Allows for chained filtering on all of the filters available on the [user resource](../users/), e.g. `history_user__username`.
      * `history_user_ip` - filter by the IP address of the editor.
      * `history_date` - filter by history date. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `history_type` - filter by [history type id](../../api_docs/history_type), exact.

    Ordering
    --------

    You can order the result set by providing the `ordering` query parameter with the value of one of:

      * `history_date`

    You can reverse ordering by using the `-` sign, e.g. `-history_date`.
    """
    queryset = PageTagSet.versions.all()
    serializer_class = HistoricalPageTagSetSerializer
    filter_class = HistoricalTagFilter
    ordering_fields = ('history_date',)


router.register(u'tags_history', HistoricalTagViewSet)
