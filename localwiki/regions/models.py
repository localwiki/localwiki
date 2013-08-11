import re
import unicodedata
from urllib import unquote_plus

from django.utils.translation import ugettext_lazy
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from django.template.defaultfilters import stringfilter

from django.contrib.gis.db import models


class Region(models.Model):
    full_name = models.CharField(max_length=255,
        help_text=ugettext_lazy("The full name of this region, e.g. 'San Francisco'"))
    slug = models.SlugField(max_length=255, unique=True,
        help_text=ugettext_lazy("A very short name for this region that will appear in URLs, e.g. 'sf'. "
            "Spaces okay, but keep it short and memorable!"))
    geom = models.MultiPolygonField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.slug)
        super(Region, self).save(*args, **kwargs)

    def populate_region(self, *args, **kwargs):
        from pages.models import Page
        from initial_data import populate_region

        if Page.objects.filter(region=self):
            raise IntegrityError(_("Region already has pages in it"))
        populate_region(self)


class RegionSettings(models.Model):
    region = models.OneToOneField(Region)
    # Can be null for the 'main' region, which may not have a geometry.
    region_center = models.PointField(null=True)
    region_zoom_level = models.IntegerField(null=True)


SLUGIFY_KEEP = r"\.-"
SLUGIFY_MISC_CHARS = re.compile(('[^\w\s%s]' % SLUGIFY_KEEP), re.UNICODE)
def slugify(value):
    """
    Normalizes region name for db lookup

    Args:
        value: String or unicode object to normalize.
    Returns:
        Lowercase string with special characters removed.
    """
    value = unquote_plus(value.encode('utf-8')).decode('utf-8')

    # normalize unicode
    value = unicodedata.normalize('NFKD', unicode(value))

    # remove non-{word,space,keep} characters
    value = re.sub(SLUGIFY_MISC_CHARS, '', value)
    value = value.strip()
    value = re.sub('[\s_]+', '-', value)

    return value.lower()
slugify = stringfilter(slugify)


# For registration calls
import signals
import api
