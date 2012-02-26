from tastypie.resources import ModelResource, ALL

from models import Page, PageFile
from sapling.api import api, SlugifyMixin


# TODO: move this under /page/<slug>/_file/<filename>?
class FileResource(ModelResource):
    class Meta:
        queryset = PageFile.objects.all()
        resource_name = 'file'
        filtering = {
            'name': ALL,
            'slug': ALL,
        }


class PageResource(SlugifyMixin, ModelResource):
    class Meta:
        queryset = Page.objects.all()
        resource_name = 'page'
        slugify_from_field = 'name'
        filtering = {
            'name': ALL,
            'slug': ALL,
        }
    

api.register(PageResource())
api.register(FileResource())
