from django.contrib.gis.db import models
from django.core.urlresolvers import reverse

from regions.models import Region
from versionutils import versioning

from fields import FlatCollectionFrom


class MapData(models.Model):
    points = models.MultiPointField(null=True, blank=True)
    lines = models.MultiLineStringField(null=True, blank=True)
    polys = models.MultiPolygonField(null=True, blank=True)
    geom = FlatCollectionFrom(points='points', lines='lines', polys='polys')
    length = models.FloatField(null=True, editable=False)

    page = models.OneToOneField('pages.Page')
    region = models.ForeignKey(Region, null=True)

    objects = models.GeoManager()

    def get_absolute_url(self):
        return reverse('maps:show',
            args=[self.region.slug, self.page.pretty_slug])

    def save(self, *args, **kwargs):
        self.length = self.geom.length
        super(MapData, self).save(*args, **kwargs)

    def exists(self):
        """
        Returns:
            True if the MapData currently exists in the database.
        """
        return MapData.objects.filter(
            page=self.page, region=self.region).exists()

versioning.register(MapData)


# For registration calls
import feeds
