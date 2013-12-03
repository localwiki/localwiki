from rest_framework import serializers

from .models import MapData


class MapDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MapData
        fields = ('url', 'page', 'region', 'points', 'lines', 'polys', 'geom', 'length')
