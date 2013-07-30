from django.contrib.gis.db import models

from maps.fields import *


class MapInfo(models.Model):
    points = models.MultiPointField(null=True, blank=True)
    lines = models.MultiLineStringField(null=True, blank=True)
    polys = models.MultiPolygonField(null=True, blank=True)
    geom = CollectionFrom(points='points', lines='lines', polys='polys')

    objects = models.GeoManager()

    class Meta:
        # http://south.aeracode.org/ticket/520
        app_label = 'utils'


TEST_MODELS = [
    MapInfo,
]
