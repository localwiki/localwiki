from tastypie.resources import ModelResource, ALL
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS

from models import Tag, PageTagSet
from main.api import api
from main.api.resources import ModelHistoryResource
from main.api.authentication import ApiKeyWriteAuthentication
from main.api.authorization import ExtendedDjangoAuthorization


# Tags can be edited if the page can be edited.
class ChangePageAuthorization(ExtendedDjangoAuthorization):
    permission_map = {
        'POST': ['pages.change_page'],
        'PUT': ['pages.change_page'],
        'DELETE': ['pages.change_page'],
        'PATCH': ['pages.change_page']
    }


class TagResource(ModelResource):
    region = fields.ForeignKey('regions.api.RegionResource', 'region', null=True, full=True)

    class Meta:
        resource_name = 'tag'
        queryset = Tag.objects.all()
        filtering = {
            'name': ALL,
            'slug': ALL,
        }
        ordering = ['name', 'slug']
        list_allowed_methods = ['get', 'post']
        authentication = ApiKeyWriteAuthentication()
        authorization = ChangePageAuthorization()

api.register(TagResource())


class PageTagSetResource(ModelResource):
    region = fields.ForeignKey('regions.api.RegionResource', 'region', null=True, full=True)
    page = fields.ToOneField('pages.api.PageResource', 'page')
    tags = fields.ToManyField(TagResource, 'tags')

    class Meta:
        resource_name = 'page_tags'
        queryset = PageTagSet.objects.all()
        filtering = {
            'page': ALL_WITH_RELATIONS,
            'tags': ALL_WITH_RELATIONS,
        }
        ordering = ['page', 'tags']
        list_allowed_methods = ['get', 'post']
        authentication = ApiKeyWriteAuthentication()
        authorization = ChangePageAuthorization()


class PageTagSetHistoryResource(ModelHistoryResource):
    region = fields.ForeignKey('regions.api.RegionResource', 'region', null=True, full=True)
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
