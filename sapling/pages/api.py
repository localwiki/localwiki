from django.conf.urls.defaults import url
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404

from tastypie.resources import ModelResource, ALL
from tastypie.utils import trailing_slash

from pages.models import Page, PageFile, slugify, name_to_url
from sapling.api import api, SlugifyMixin


class PageSlugifyMixin(SlugifyMixin):
    """
    A version of SlugifyMixin that uses our custom slugify and quotes
    URLs using our name_to_url. We need this because we aren't using
    the standard slugify with our page-related models, and we also want
    our page-related Resources to have urls_with_underscores.
    """
    def __init__(self, *args, **kwargs):
        self._meta.lookup_function = slugify
        self._meta.to_url_function = name_to_url
        super(PageSlugifyMixin, self).__init__(*args, **kwargs)


# TODO: move this under /page/<slug>/_file/<filename>?
class FileResource(ModelResource):
    class Meta:
        queryset = PageFile.objects.all()
        resource_name = 'file'
        filtering = {
            'name': ALL,
            'slug': ALL,
        }


class FileHistoryResource(FileResource):
    class Meta:
        resource_name = 'file_version'
        queryset = PageFile.versions.all()


class PageResource(PageSlugifyMixin, ModelResource):
    class Meta:
        queryset = Page.objects.all()
        resource_name = 'page'
        field_to_slugify = 'name'
        filtering = {
            'name': ALL,
            'slug': ALL,
        }

    def override_urls(self):
        # For searching.
        l = [
            url(r"^(?P<resource_name>%s)/search%s$" %
                (self._meta.resource_name, trailing_slash()),
                 self.wrap_view('get_search'), name="api_get_search"),
        ]
        # and get the base class' URLs (our slug stuff)
        l += super(PageResource, self).override_urls()
        return l

    def get_search(self, request, **kwargs):
        """
        A simple search method, mostly from the tastypie examples.
        """
        from haystack.query import SearchQuerySet
        # The search method isn't discoverable via the API.  TODO: Fix that.

        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # Do the query.
        sqs = SearchQuerySet().models(Page).load_all().auto_query(
            request.GET.get('q', ''))
        paginator = Paginator(sqs, 20)

        try:
            page = paginator.page(int(request.GET.get('page', 1)))
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")

        objects = []

        for result in page.object_list:
            if not result:
                continue
            bundle = self.build_bundle(obj=result.object, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {'objects': objects}

        self.log_throttled_access(request)
        return self.create_response(request, object_list)


# We don't use the PageSlugifyMixin approach here because it becomes
# too complicated to generate pretty URLs with the historical version
# identifiers.
class PageHistoryResource(ModelResource):
    class Meta:
        resource_name = 'page_version'
        queryset = Page.versions.all()
        filtering = {
            'name': ALL,
            'slug': ALL,
        }


api.register(PageResource())
api.register(PageHistoryResource())
api.register(FileResource())
api.register(FileHistoryResource())
