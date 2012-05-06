from tastypie.resources import ModelResource, ALL
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS

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


class PageTagSetResource(SlugifyMixin, ModelResource):
    page = fields.ToOneField(pages.api.PageResource, 'page')
    tags = fields.ToManyField(TagResource, 'tags')

    class Meta:
        resource_name = 'page_tag_set'
        queryset = PageTagSet.objects.all()
        field_to_slugify = 'page'
        slug_lookup_field = 'page__slug'
        lookup_function = slugify
        filtering = {
            'page': ALL_WITH_RELATIONS,
            'tags': ALL_WITH_RELATIONS,
        }

api.register(PageTagSetResource())
