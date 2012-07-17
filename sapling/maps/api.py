from tastypie import fields
from tastypie.resources import ALL
from tastypie.contrib.gis.resources import ModelResource

from models import MapData
import pages.api  # Scoped import to prevent ImportError.
from sapling.api import api


class MapResource(pages.api.PageSlugifyMixin, ModelResource):
    page = fields.ToOneField(pages.api.PageResource, 'page')

    class Meta:
        queryset = MapData.objects.all()
        resource_name = 'map'
        field_to_slugify = 'page'
        slug_lookup_field = 'page__slug'
        filtering = {
            'points': ALL,
            'lines': ALL,
            'polys': ALL,
            'geom': ALL,
            'length': ALL,
        }


# We don't use the PageSlugifyMixin approach here because it becomes
# too complicated to generate pretty URLs with the historical version
# identifiers.
class MapHistoryResource(ModelResource):
    page = fields.ToOneField(pages.api.PageHistoryResource, 'page')

    class Meta:
        queryset = MapData.versions.all()
        resource_name = 'map_version'
        filtering = {
            'points': ALL,
            'lines': ALL,
            'polys': ALL,
            'geom': ALL,
            'length': ALL,
        }


api.register(MapResource())
api.register(MapHistoryResource())
