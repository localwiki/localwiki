from django.contrib.gis.db import models

from versionutils import diff
from versionutils.versioning import TrackChanges
from pages.models import Page
from validators import validate_geometry


# TODO: Maybe move this into pages/models.py?
class MapData(models.Model):
    geom = models.GeometryCollectionField(validators=[validate_geometry])
    page = models.OneToOneField(Page)

    objects = models.GeoManager()
    history = TrackChanges()


class MapDiff(diff.BaseModelDiff):
    fields = (
        ('geom', diff.diffutils.GeometryFieldDiff),
    )

diff.register(MapData, MapDiff)
