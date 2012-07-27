from tastypie.resources import ModelResource, ALL
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization

from models import Tag, PageTagSet
import pages
from sapling.api import api
from sapling.api.authentication import ApiKeyWriteAuthentication


class TagResource(ModelResource):
    class Meta:
        resource_name = 'tags'
        queryset = Tag.objects.all()
        detail_uri_name = 'slug'
        filtering = {
            'name': ALL,
            'slug': ALL,
        }

api.register(TagResource())


class PageTagSetResource(pages.api.PageURLMixin, ModelResource):
    page = fields.ToOneField(pages.api.PageResource, 'page')
    tags = fields.ToManyField(TagResource, 'tags')

    class Meta:
        resource_name = 'page_tags'
        queryset = PageTagSet.objects.all()
        detail_uri_name = 'page__name'
        filtering = {
            'page': ALL_WITH_RELATIONS,
            'tags': ALL_WITH_RELATIONS,
        }
        list_allowed_methods = ['get', 'post']
        authentication = ApiKeyWriteAuthentication()
        authorization = DjangoAuthorization()


# We don't use detail_uri_name here because it becomes too complicated
# to generate pretty URLs with the historical version identifers.
# TODO: Fix this. Maybe easier now with `detail_uri_name` and the uri prep
# method.
class PageTagSetHistoryResource(ModelResource):
    page = fields.ToOneField(pages.api.PageHistoryResource, 'page')
    tags = fields.ToManyField(TagResource, 'tags')

    class Meta:
        resource_name = 'page_tag_set_version'
        queryset = PageTagSet.versions.all()
        filtering = {
            'page': ALL_WITH_RELATIONS,
            'tags': ALL_WITH_RELATIONS,
        }

api.register(PageTagSetResource())
api.register(PageTagSetHistoryResource())
