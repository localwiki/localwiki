from django.contrib.auth.models import User
from django import forms

from rest_framework import viewsets
from rest_framework_filters import FilterSet, filters
from rest_framework_gis.filters import GeoFilterSet

from main.api import router
from main.api.filters import HistoricalFilter
from main.api.views import AllowFieldLimitingMixin
from tags.models import Tag, PageTagSet, slugify as tag_slugify
from versionutils.versioning.constants import TYPE_CHOICES
from regions.api import RegionFilter
from users.api import UserFilter

from .models import Page, PageFile, slugify
from .serializers import (PageSerializer, HistoricalPageSerializer,
    FileSerializer, HistoricalFileSerializer)


class PagePermissionsMixin(object):
    """
    This mixin will cause a view's edit permissions to depend on the Page
    model rather than just on the view's `model` attribute.

    By default, our API views will use the per-object permission for the 
    model specified by the view's `model` attribute.  However, sometimes we
    want to also depend on other permissions.
    """
    def get_perms_required(self, request_method, obj=None):
        perms_map = {
            'GET': [],
            'OPTIONS': [],
            'HEAD': [],
            'POST': ['pages.change_page'],
            'PUT': ['pages.change_page'],
            'PATCH': ['pages.change_page'],
            'DELETE': ['pages.change_page'],
        }
        return perms_map[request_method]

    def get_protected_object(self, obj):
        return obj.page

    def get_protected_objects(self, obj):
        return [self.get_protected_object(obj)]

    def check_permissions(self, request):
        super(PagePermissionsMixin, self).check_permissions(request)
        perms_required = self.get_perms_required(request.method)
        if not request.user.has_perms(perms_required):
            self.permission_denied(request)
    
    def check_object_permissions(self, request, obj):
        super(PagePermissionsMixin, self).check_object_permissions(request, obj)
        objs = self.get_protected_objects(obj)
        for obj in objs:
            perms_required = self.get_perms_required(request.method, obj=obj)
            if not request.user.has_perms(perms_required, obj):
                self.permission_denied(request)

    def pre_save(self, obj):
        # We have to include a `pre_save` method here because
        # otherwise there's no per-object check on POST, which
        # never calls `check_object_permissions`.
        self.check_object_permissions(self.request, obj)


def get_or_create_tag(word, region):
    tag, created = Tag.objects.get_or_create(
        slug=tag_slugify(word), region=region,
        defaults={'name': word}
    )
    return tag


class TagFilter(filters.Filter):
    def filter(self, qs, value):
        value = value.strip()
        if not value:
            return qs
        for v in value.split(','):
            join_on = ''
            if getattr(self, 'parent_relation', None):
                join_on = '%s__' % self.parent_relation
            kws = {'%spagetagset__tags__slug' % join_on: v}
            qs = qs.filter(**kws)
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


class PageViewSet(AllowFieldLimitingMixin, viewsets.ModelViewSet):
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
      * `slug` -- Filter by page `slug`. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.
      * `tags` -- Filter by tag.  E.g. `tags=park` for all pages tagged 'park', or `tags=park,wifi` for all pages tagged 'park' **and** also tagged 'wifi'.

    Ordering
    --------

    You can order the result set by providing the `ordering` query parameter with the value of one of:

      * `slug`

    You can reverse ordering by using the `-` sign, e.g. `-slug`.
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    filter_class = PageFilter
    ordering_fields = ('slug',)

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


class HistoricalPageViewSet(AllowFieldLimitingMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing page history.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `name` -- Filter by name, exact.
      * `slug` -- Filter by page `slug`. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.

    And the usual set of historical filter fields:

      * `history_user` - filter by the `user` resource of the editor, if user was logged in.  Allows for chained filtering on all of the filters available on the [user resource](../users/), e.g. `history_user__username`.
      * `history_user_ip` - filter by the IP address of the editor.
      * `history_date` - filter by history date. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `history_type` - filter by [history type id](../../api_docs/history_type), exact.

    Ordering
    --------

    You can order the result set by providing the `ordering` query parameter with the value of one of:

      * `slug`
      * `history_date`

    You can reverse ordering by using the `-` sign, e.g. `-slug`.
    """
    queryset = Page.versions.all()
    serializer_class = HistoricalPageSerializer
    filter_class = HistoricalPageFilter
    ordering_fields = ('slug', 'history_date')


class FileFilter(GeoFilterSet, FilterSet):
    slug = filters.AllLookupsFilter(name='slug')
    region = filters.RelatedFilter(RegionFilter, name='region')

    class Meta:
        model = PageFile
        fields = ('name', 'slug')


class HistoricalFileFilter(FileFilter, HistoricalFilter):
    class Meta:
        model = PageFile.versions.model


class FileViewSet(PagePermissionsMixin, AllowFieldLimitingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows files to be viewed and edited.  For information on
    uploading files via the API, see [the documentation](http://localwiki.net/main/API_Documentation#uploading_files).

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `name` -- Filter by file name, exact.
      * `slug` -- Filter by page `slug`. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.

    Ordering
    --------

    You can order the result set by providing the `ordering` query parameter with the value of one of:

      * `slug`

    You can reverse ordering by using the `-` sign, e.g. `-slug`.
    """
    queryset = PageFile.objects.all()
    serializer_class = FileSerializer
    filter_class = FileFilter
    ordering_fields = ('slug',)

    def get_protected_object(self, obj):
        pgs = Page.objects.filter(slug=obj.slug, region=obj.region)
        if pgs:
            return pgs[0]


class HistoricalFileViewSet(AllowFieldLimitingMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing file history.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `name` -- Filter by name, exact.
      * `slug` -- Filter by page `slug`. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `region` -- Filter by region.  Allows for chained filtering on all of the filters available on the [region resource](../regions/), e.g. `region__slug`.

    And the usual set of historical filter fields:

      * `history_user` - filter by the `user` resource of the editor, if user was logged in.  Allows for chained filtering on all of the filters available on the [user resource](../users/), e.g. `history_user__username`.
      * `history_user_ip` - filter by the IP address of the editor.
      * `history_date` - filter by history date. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `history_type` - filter by [history type id](../../api_docs/history_type), exact.

    Ordering
    --------

    You can order the result set by providing the `ordering` query parameter with the value of one of:

      * `slug`
      * `history_date`

    You can reverse ordering by using the `-` sign, e.g. `-slug`.
    """
    queryset = PageFile.versions.all()
    serializer_class = HistoricalFileSerializer
    filter_class = HistoricalFileFilter
    ordering_fields = ('slug', 'history_date')




router.register(u'pages', PageViewSet)
router.register(u'pages_history', HistoricalPageViewSet)
router.register(u'files', FileViewSet)
router.register(u'files_history', HistoricalFileViewSet)
