from django.contrib.auth.models import User
from django import forms

from rest_framework import viewsets
from rest_framework_filters import FilterSet, filters
from rest_framework_gis.filters import GeoFilterSet

from main.api import router
from main.api.filters import HistoricalFilter
from tags.models import Tag, PageTagSet, slugify
from versionutils.versioning.constants import TYPE_CHOICES
from regions.api import RegionFilter
from users.api import UserFilter

from .models import Page, PageFile
from .serializers import (PageSerializer, HistoricalPageSerializer,
    FileSerializer, HistoricalFileSerializer)

def get_or_create_tag(word, region):
    tag, created = Tag.objects.get_or_create(
        slug=slugify(word), region=region,
        defaults={'name': word}
    )
    return tag


class TagFilter(filters.Filter):
    def filter(self, qs, value):
        value = value.strip()
        if not value:
            return qs
        for v in value.split(','):
            qs = qs.filter(pagetagset__tags__slug=v)
        return qs


class PageFilter(GeoFilterSet, FilterSet):
    slug = filters.AllLookupsFilter(name='slug')
    region = filters.RelatedFilter(RegionFilter, name='region')
    tags = TagFilter()

    class Meta:
        model = Page
        fields = ('name', 'slug')


class HistoricalPageFilter(PageFilter, HistoricalFilter):
    class Meta:
        model = Page.versions.model


class PageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows pages to be viewed and edited.

    Tags
    ---------------------

    Tags can be found in the `tags` attribute.  You can update
    *just* the tags by issuing a `PATCH` here with just the `tags`
    attribute present, e.g.:

        {"tags": ["park", "fun"]}

    To update a page and not change the tags, simply exclude the
    `tags` field from your update.

    To delete all tags from the page, issue a request with  `tags`
    set to `[]`.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `name` -- Filter by name, exact.
      * `slug` -- Filter by page `slug`. Supports the [standard lookup types](../../api_docs/filters)
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.
      * `tags` -- Filter by tag.  E.g. `tags=park` for all pages tagged 'park', or `tags=park,wifi` for all pages tagged 'park' **and** also tagged 'wifi'.
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    filter_class = PageFilter

    def post_save(self, page, *args, **kwargs):
        if not hasattr(page, '_tags'):
            # Not providing any tag detail, so let's skip altering the tags.
            return

        if type(page._tags) is list:
            # If tags were provided in the request
            try:
                pts = PageTagSet.objects.get(page=page, region=page.region)
            except PageTagSet.DoesNotExist:
                pts = PageTagSet(page=page, region=page.region)
            pts.save()

            tags = []
            for word in page._tags:
                tags.append(get_or_create_tag(word, page.region))
            pts.tags = tags


class HistoricalPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing page history.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `name` -- Filter by name, exact.
      * `slug` -- Filter by page `slug`. Supports the [standard lookup types](../../api_docs/filters)
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.

    And the usual set of historical filter fields:

      * `history_user` - filter by the `user` resource of the editor, if user was logged in.  Allows for chained filtering on all of the filters available on the [user resource](../users/), e.g. `history_user__username`.
      * `history_user_ip` - filter by the IP address of the editor.
      * `history_date` - filter by history date. Supports the [standard lookup types](../../api_docs/filters)
      * `history_type` - filter by [history type id](../../api_docs/history_type), exact.
    """
    queryset = Page.versions.all()
    serializer_class = HistoricalPageSerializer
    filter_class = HistoricalPageFilter


class FileFilter(GeoFilterSet, FilterSet):
    slug = filters.AllLookupsFilter(name='slug')
    region = filters.RelatedFilter(RegionFilter, name='region')

    class Meta:
        model = PageFile
        fields = ('name', 'slug')


class HistoricalFileFilter(FileFilter, HistoricalFilter):
    class Meta:
        model = PageFile.versions.model


class FileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows files to be viewed and edited.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `name` -- Filter by file name, exact.
      * `slug` -- Filter by page `slug`. Supports the [standard lookup types](../../api_docs/filters)
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.
    """
    queryset = PageFile.objects.all()
    serializer_class = FileSerializer
    filter_class = FileFilter


class HistoricalFileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing file history.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `name` -- Filter by name, exact.
      * `slug` -- Filter by page `slug`. Supports the [standard lookup types](../../api_docs/filters)
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.

    And the usual set of historical filter fields:

      * `history_user` - filter by the `user` resource of the editor, if user was logged in.  Allows for chained filtering on all of the filters available on the [user resource](../users/), e.g. `history_user__username`.
      * `history_user_ip` - filter by the IP address of the editor.
      * `history_date` - filter by history date. Supports the [standard lookup types](../../api_docs/filters)
      * `history_type` - filter by [history type id](../../api_docs/history_type), exact.
    """
    queryset = PageFile.versions.all()
    serializer_class = HistoricalFileSerializer
    filter_class = HistoricalFileFilter


router.register(u'pages', PageViewSet)
router.register(u'pages_history', HistoricalPageViewSet)
router.register(u'files', FileViewSet)
router.register(u'files_history', HistoricalFileViewSet)
