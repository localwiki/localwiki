from urllib import urlencode

from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404, HttpResponseRedirect

from tastypie import http
from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.validation import Validation
from tastypie.authorization import DjangoAuthorization
from tastypie.utils import trailing_slash

from redirects.models import Redirect
from main.api import api
from main.api.resources import ModelHistoryResource
from main.api.authentication import ApiKeyWriteAuthentication

from models import Page, PageFile, name_to_url, url_to_name, clean_name


class PageValidation(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        pagename = bundle.data.get('name')
        if pagename:
            if pagename != clean_name(pagename):
                errors['name'] = ['Pagename cannot contain underscores or '
                    'a / character surrounded by spaces. Please replace '
                    'underscores with spaces and remove spaces surrounding the'
                    ' / character.'
                ]
        return errors


# TODO: move this under /page/<slug>/_file/<filename>?
class FileResource(ModelResource):
    region = fields.ForeignKey('regions.api.RegionResource', 'region', null=True, full=True)

    class Meta:
        queryset = PageFile.objects.all()
        resource_name = 'file'
        filtering = {
            'name': ALL,
            'slug': ALL,
        }
        ordering = ['name', 'slug']
        list_allowed_methods = ['get', 'post']
        authentication = ApiKeyWriteAuthentication()
        authorization = DjangoAuthorization()


class FileHistoryResource(FileResource, ModelHistoryResource):
    region = fields.ForeignKey('regions.api.RegionResource', 'region', null=True, full=True)

    class Meta:
        resource_name = 'file_version'
        queryset = PageFile.versions.all()
        filtering = {
            'name': ALL,
            'slug': ALL,
            'history_date': ALL,
            'history_type': ALL,
        }
        ordering = ['history_date']


class PageResource(ModelResource):
    region = fields.ForeignKey('regions.api.RegionResource', 'region', null=True, full=True)
    map = fields.ToOneField('maps.api.MapResource', 'mapdata', null=True,
        readonly=True)
    page_tags = fields.ToOneField('tags.api.PageTagSetResource', 'pagetagset',
        null=True, readonly=True)

    class Meta:
        queryset = Page.objects.all()
        resource_name = 'page'
        filtering = {
            'name': ALL,
            'slug': ALL,
            'page_tags': ALL_WITH_RELATIONS,
            'map': ALL_WITH_RELATIONS,
        }
        list_allowed_methods = ['get', 'post']
        ordering = ['name', 'slug']
        validation = PageValidation()
        authentication = ApiKeyWriteAuthentication()
        authorization = DjangoAuthorization()

    def prepend_urls(self):
        # For searching.
        l = [
            url(r"^(?P<resource_name>%s)/search%s$" %
                (self._meta.resource_name, trailing_slash()),
                 self.wrap_view('get_search'), name="api_get_search"),
        ]
        # and get the base class' URLs
        l += super(PageResource, self).prepend_urls()
        return l

    def get_detail(self, request, **kwargs):
        resp = super(PageResource, self).get_detail(request, **kwargs)
        if not isinstance(resp, http.HttpNotFound):
            return resp
        # check if the page has been redirected
        try:
            obj = Redirect.objects.get(
                source=self.remove_api_resource_names(kwargs)['name']
            ).destination
            redirect_url = (self.get_resource_uri(obj) + 
                            '?' + urlencode(request.GET))
            return HttpResponseRedirect(redirect_url)
        except ObjectDoesNotExist:
            return resp

        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)
        return self.create_response(request, bundle)

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

    def dehydrate(self, bundle):
        in_page_api = False
        for pattern in self.urls:
            if pattern.resolve(bundle.request.path.replace('/api/', '')):
                in_page_api = True
        if (not in_page_api and not bundle.request.GET.get('full')):
            bundle = bundle.data['resource_uri']
        return bundle


class PageHistoryResource(ModelHistoryResource):
    region = fields.ForeignKey('regions.api.RegionResource', 'region', null=True, full=True)

    class Meta:
        resource_name = 'page_version'
        queryset = Page.versions.all()
        filtering = {
            'name': ALL,
            'slug': ALL,
            'history_date': ALL,
            'history_type': ALL,
        }
        ordering = ['history_date']


api.register(PageResource())
api.register(PageHistoryResource())
api.register(FileResource())
api.register(FileHistoryResource())
