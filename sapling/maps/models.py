from django.contrib.gis.db import models
from django.contrib.gis.geos import *
from django.core.urlresolvers import reverse

from versionutils import versioning
from pages.models import Page

from fields import *


class MapData(models.Model):
    points = models.MultiPointField(null=True, blank=True)
    lines = models.MultiLineStringField(null=True, blank=True)
    polys = models.MultiPolygonField(null=True, blank=True)
    geom = FlatCollectionFrom(points='points', lines='lines', polys='polys')
    length = models.FloatField(null=True, editable=False)

    page = models.OneToOneField(Page)

    objects = models.GeoManager()

    def get_absolute_url(self):
        return reverse('maps:show', args=[self.page.pretty_slug])

    def save(self, *args, **kwargs):
        self.length = self.geom.length
        super(MapData, self).save(*args, **kwargs)

    def exists(self):
        """
        Returns:
            True if the MapData currently exists in the database.
        """
        if MapData.objects.filter(page=self.page):
            return True
        return False

versioning.register(MapData)

import feeds # To fire register() calls.
