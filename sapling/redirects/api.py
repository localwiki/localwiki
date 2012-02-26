from tastypie.resources import ModelResource, ALL
from tastypie import fields

from models import Redirect
from pages.api import PageResource
from sapling.api import api, SlugifyMixin


class RedirectResource(SlugifyMixin, ModelResource):
    destination = fields.ForeignKey(PageResource, 'destination')
    class Meta:
        queryset = Redirect.objects.all()
        slug_lookup_field = 'source'
        filtering = {
            'destination': ALL,
            'source': ALL,
        }
    

api.register(RedirectResource())
