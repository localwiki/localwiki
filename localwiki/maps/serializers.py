from rest_framework import serializers

from localwiki.utils.serializers import HISTORY_FIELDS

from .models import MapData


class MapDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MapData
        fields = ('url', 'page', 'region', 'points', 'lines', 'polys', 'geom', 'length')


class HistoricalMapDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MapData.versions.model
        fields = (('url', 'page', 'region', 'points', 'lines', 'polys', 'geom', 'length') +
                  HISTORY_FIELDS)
