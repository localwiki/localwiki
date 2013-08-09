from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ALL, ALL_WITH_RELATIONS
from tastypie.contrib.gis import resources as gis_resources

from models import MapData
from main.api import api
from main.api.resources import ModelHistoryResource
from main.api.authentication import ApiKeyWriteAuthentication


class MapResource(gis_resources.ModelResource):
    region = fields.ForeignKey('regions.api.RegionResource', 'region', null=True, full=True)
    page = fields.ToOneField('pages.api.PageResource', 'page', full=True)

    class Meta:
        queryset = MapData.objects.all()
        resource_name = 'map'
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


class MapHistoryResource(gis_resources.ModelResource, ModelHistoryResource):
    region = fields.ForeignKey('regions.api.RegionResource', 'region', null=True, full=True)
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
