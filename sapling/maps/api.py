from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ALL, ALL_WITH_RELATIONS
from tastypie.contrib.gis import resources as gis_resources

from models import MapData
import pages.api  # Scoped import to prevent ImportError.
from sapling.api import api
from sapling.api.resources import ModelHistoryResource
from sapling.api.authentication import ApiKeyWriteAuthentication


class MapResource(pages.api.PageURLMixin, gis_resources.ModelResource):
    page = fields.ToOneField('pages.api.PageResource', 'page', full=True)

    class Meta:
        queryset = MapData.objects.all()
        resource_name = 'map'
        detail_uri_name = 'page__name'
        filtering = {
            'page': ALL_WITH_RELATIONS,
            'points': ALL,
            'lines': ALL,
            'polys': ALL,
            'geom': ALL,
            'length': ALL,
        }
        list_allowed_methods = ['get', 'post']
        authentication = ApiKeyWriteAuthentication()
        authorization = DjangoAuthorization()


# We don't use detail_uri_name here because it becomes too complicated
# to generate pretty URLs with the historical version identifers.
# TODO: Fix this. Maybe easier now with `detail_uri_name` and the uri prep
# method.
class MapHistoryResource(gis_resources.ModelResource, ModelHistoryResource):
    page = fields.ToOneField('pages.api.PageHistoryResource', 'page')

    class Meta:
        queryset = MapData.versions.all()
        resource_name = 'map_version'
        filtering = {
            'page': ALL_WITH_RELATIONS,
            'points': ALL,
            'lines': ALL,
            'polys': ALL,
            'geom': ALL,
            'length': ALL,
            'history_date': ALL,
            'history_type': ALL,
        }
        ordering = ['history_date']


api.register(MapResource())
api.register(MapHistoryResource())
