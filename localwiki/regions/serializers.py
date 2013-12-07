from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework_gis.serializers import GeoModelSerializer

from .models import Region, RegionSettings


class RegionSettingsSerializer(GeoModelSerializer, HyperlinkedModelSerializer):
    class Meta:
        model = RegionSettings
        fields = ('region_center', 'region_zoom_level', 'default_language')


class RegionSerializer(GeoModelSerializer, HyperlinkedModelSerializer):
    settings = RegionSettingsSerializer(source='regionsettings')

    class Meta:
        model = Region
        fields = ('url', 'slug', 'full_name', 'geom', 'settings')
