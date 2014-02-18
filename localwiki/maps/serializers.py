from rest_framework import serializers
from rest_framework_gis.serializers import GeoModelSerializer

from localwiki.main.api.fields import HISTORY_FIELDS

from .models import MapData


class MapDataSerializer(GeoModelSerializer, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MapData
        fields = ('url', 'page', 'region', 'points', 'lines', 'polys', 'geom', 'length')


class HistoricalMapDataSerializer(GeoModelSerializer, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MapData.versions.model
        fields = (('url', 'page', 'region', 'points', 'lines', 'polys', 'geom', 'length') +
                  HISTORY_FIELDS)
