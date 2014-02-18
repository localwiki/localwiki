from rest_framework import viewsets
from rest_framework_filters import filters, FilterSet
from rest_framework_gis.filters import GeoFilterSet

from main.api import router
from main.api.filters import HistoricalFilter
from main.api.views import AllowFieldLimitingMixin
from pages.models import Page
from pages.api import PageFilter, PagePermissionsMixin
from regions.api import RegionFilter

from .models import Redirect
from .serializers import RedirectSerializer, HistoricalRedirectSerializer


class RedirectFilter(GeoFilterSet, FilterSet):
    source = filters.AllLookupsFilter(name='source')
    destination = filters.RelatedFilter(PageFilter, name='destination')
    region = filters.RelatedFilter(RegionFilter, name='region')

    class Meta:
        model = Redirect


class HistoricalRedirectFilter(RedirectFilter, HistoricalFilter):
    class Meta:
        model = Redirect.versions.model


class RedirectPermissionsMixin(PagePermissionsMixin):
    """
    We want to tie the redirect permissions should be tied to the Redirect
    object -and- the Page object that's associated with the redirect. This
    is so that if, for instance, Page(name="Front Page") is only editable
    by a certain group, creating a Redirect from "Front Page" to somewhere
    is similarly protected.
    """
    def get_protected_objects(self, obj):
        protected = []

        page = Page.objects.filter(slug=obj.source, region=obj.region)
        if page:
            protected.append(page[0])
        redirect = Redirect.objects.filter(source=obj.source, region=obj.region)
        if redirect:
            protected.append(redirect[0])

        return protected

    def get_perms_required(self, request_method, obj=None):
        if isinstance(obj, Page):
            perms_map = {
                'GET': [],
                'OPTIONS': [],
                'HEAD': [],
                'POST': ['pages.change_page'],
                'PUT': ['pages.change_page'],
                'PATCH': ['pages.change_page'],
                'DELETE': ['redirects.delete_redirect'],
            }
        else:
            perms_map = {
                'GET': [],
                'OPTIONS': [],
                'HEAD': [],
                'POST': ['redirects.change_redirect'],
                'PUT': ['redirects.change_redirect'],
                'PATCH': ['redirects.change_redirect'],
                'DELETE': ['redirects.delete_redirect'],
            }

        return perms_map[request_method]


class RedirectViewSet(RedirectPermissionsMixin, AllowFieldLimitingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows redirects to be viewed and edited.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `source` -- Filter by source slug. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `destination` -- Filter by destination page.  Allows for chained filtering on all of the filters available on the [page resource](../pages/), e.g. `destination__slug`.
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.

    Ordering
    --------

    You can order the result set by providing the `ordering` query parameter with the value of one of:

      * `source`

    You can reverse ordering by using the `-` sign, e.g. `-source`.
    """
    queryset = Redirect.objects.all()
    serializer_class = RedirectSerializer
    filter_class = RedirectFilter
    ordering_fields = ('source',)


class HistoricalRedirectViewSet(AllowFieldLimitingMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows redirect history to be viewed.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `source` -- Filter by source slug. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `destination` -- Filter by destination page.  Allows for chained filtering on all of the filters available on the [page resource](../pages/), e.g. `destination__slug`.
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.

    And the usual set of historical filter fields:

      * `history_user` - filter by the `user` resource of the editor, if user was logged in.  Allows for chained filtering on all of the filters available on the [user resource](../users/), e.g. `history_user__username`.
      * `history_user_ip` - filter by the IP address of the editor.
      * `history_date` - filter by history date. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `history_type` - filter by [history type id](../../api_docs/history_type), exact.

    Ordering
    --------

    You can order the result set by providing the `ordering` query parameter with the value of one of:

      * `source`
      * `history_date`

    You can reverse ordering by using the `-` sign, e.g. `-source`.
    """
    queryset = Redirect.versions.all()
    serializer_class = HistoricalRedirectSerializer
    filter_class = HistoricalRedirectFilter
    ordering_fields = ('source', 'history_date')


router.register(u'redirects', RedirectViewSet)
router.register(u'redirects_history', HistoricalRedirectViewSet)
