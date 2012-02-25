from tastypie.resources import ModelResource

from models import Page
from sapling.api import api


class PageResource(ModelResource):
    class Meta:
        queryset = Page.objects.all()
        resource_name = 'page'

api.register(PageResource())
