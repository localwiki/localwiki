from tastypie.resources import ModelResource, ALL
from tastypie import fields

from models import Tag, PageTagSet, slugify
import pages
from sapling.api import api, SlugifyMixin


class TagResource(SlugifyMixin, ModelResource):
    class Meta:
        resource_name = 'tags'
        queryset = Tag.objects.all()
        filtering = {
            'name': ALL,
            'slug': ALL,
        }
        field_to_slugify = 'name'
        lookup_function = slugify

api.register(TagResource())


class PageTagSetResource(ModelResource):
    page = fields.ToOneField(pages.api.PageResource, 'page')
    tags = fields.ToManyField(TagResource, 'tags')

    class Meta:
        resource_name = 'page_tag_set'
        queryset = PageTagSet.objects.all()

api.register(PageTagSetResource())
