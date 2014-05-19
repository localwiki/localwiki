from django.db.models.signals import post_save

from frontpage.models import FrontPage

from .models import Region, RegionSettings
from .map_utils import get_zoom_for_extent


def setup_region_settings(sender, instance, created, raw, **kwargs):
    if raw:
        # Don't create RegionSettings when importing via loaddata - they're already
        # being imported.
        return
    region_settings = RegionSettings.objects.filter(region=instance)
    if region_settings:
        region_settings = region_settings[0]
    else:
        region_settings = RegionSettings(region=instance)
    
    if instance.geom:
        region_settings.region_center = instance.geom.centroid
        region_settings.region_zoom_level = get_zoom_for_extent(instance.geom.envelope)

    region_settings.save()


def create_front_page(sender, instance, created, raw, **kwargs):
    if raw:
        # Don't create FrontPage when importing via loaddata - it's already
        # being imported.
        return
    frontpage = FrontPage.objects.filter(region=instance)
    if not frontpage:
        frontpage = FrontPage(region=instance)
        frontpage.save()


post_save.connect(setup_region_settings, sender=Region)
post_save.connect(create_front_page, sender=Region)
