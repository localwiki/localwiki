from tastypie import fields
from tastypie.resources import ModelResource

from models import MapData
import pages.api  # Scoped import to prevent ImportError.
from sapling.api import api, SlugifyMixin


class MapResource(SlugifyMixin, ModelResource):
    page = fields.ToOneField(pages.api.PageResource, 'page')

    class Meta:
        queryset = MapData.objects.all()
        resource_name = 'map'
        field_to_slugify = 'page'
        slug_lookup_field = 'page__slug'

api.register(MapResource())
