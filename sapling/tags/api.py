from tastypie.resources import ModelResource, ALL
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS

from models import Tag, PageTagSet
from pages.api import PageURLMixin
from sapling.api import api
from sapling.api.resources import ModelHistoryResource
from sapling.api.authentication import ApiKeyWriteAuthentication
from sapling.api.authorization import ExtendedDjangoAuthorization


# Tags can be edited if the page can be edited.
class ChangePageAuthorization(ExtendedDjangoAuthorization):
    permission_map = {
        'POST': ['pages.change_page'],
        'PUT': ['pages.change_page'],
        'DELETE': ['pages.change_page'],
        'PATCH': ['pages.change_page']
    }


class TagResource(ModelResource):
    class Meta:
        resource_name = 'tag'
        queryset = Tag.objects.all()
        detail_uri_name = 'slug'
        filtering = {
            'name': ALL,
            'slug': ALL,
        }
        ordering = ['name', 'slug']
        list_allowed_methods = ['get', 'post']
        authentication = ApiKeyWriteAuthentication()
        authorization = ChangePageAuthorization()

api.register(TagResource())


class PageTagSetResource(PageURLMixin, ModelResource):
    page = fields.ToOneField('pages.api.PageResource', 'page')
    tags = fields.ToManyField(TagResource, 'tags')

    class Meta:
        resource_name = 'page_tags'
        queryset = PageTagSet.objects.all()
        detail_uri_name = 'page__name'
        filtering = {
            'page': ALL_WITH_RELATIONS,
            'tags': ALL_WITH_RELATIONS,
        }
        ordering = ['page', 'tags']
        list_allowed_methods = ['get', 'post']
        authentication = ApiKeyWriteAuthentication()
        authorization = ChangePageAuthorization()


# We don't use detail_uri_name here because it becomes too complicated
# to generate pretty URLs with the historical version identifers.
# TODO: Fix this. Maybe easier now with `detail_uri_name` and the uri prep
# method.
class PageTagSetHistoryResource(ModelHistoryResource):
    page = fields.ToOneField('pages.api.PageHistoryResource', 'page')
    tags = fields.ToManyField(TagResource, 'tags')

    class Meta:
        resource_name = 'page_tag_set_version'
        queryset = PageTagSet.versions.all()
        filtering = {
            'page': ALL_WITH_RELATIONS,
            'tags': ALL_WITH_RELATIONS,
            'history_type': ALL,
            'history_date': ALL,
        }
        ordering = ['history_date']

api.register(PageTagSetResource())
api.register(PageTagSetHistoryResource())
