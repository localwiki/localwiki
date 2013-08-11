from django.db.models.signals import post_save

from models import Region, RegionSettings
from map_utils import get_zoom_for_extent


def setup_region_settings(sender, instance, created, raw, **kwargs):
    if raw:
        # Don't create RegionSettings when importing via loaddata - they're already
        # being imported.
        return
    region_settings = RegionSettings.objects.filter(region=instance)
    if not region_settings:
        region_settings = RegionSettings(region=instance)
    if instance.geom:
        region_settings.region_center = instance.geom.centroid
        region_settings.region_zoom_level = get_zoom_for_extent(instance.geom.envelope)

    region_settings.save()


post_save.connect(setup_region_settings, sender=Region)
