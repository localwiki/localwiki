from rest_framework import serializers

from .models import Region, RegionSettings


class RegionSettingsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RegionSettings
        fields = ('region_center', 'region_zoom_level', 'default_language')


class RegionSerializer(serializers.HyperlinkedModelSerializer):
    settings = RegionSettingsSerializer(source='regionsettings')

    class Meta:
        model = Region
        fields = ('url', 'slug', 'full_name', 'geom', 'settings')
