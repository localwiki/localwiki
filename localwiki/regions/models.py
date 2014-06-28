import re
import unicodedata
from urllib import unquote_plus

from django.db import IntegrityError
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template.defaultfilters import stringfilter
from django.contrib.gis.db import models

from django_randomfilenamestorage.storage import (
    RandomFilenameFileSystemStorage)


class Region(models.Model):
    full_name = models.CharField(max_length=255,
        help_text=ugettext_lazy("The full name of this region, e.g. 'San Francisco'"))
    slug = models.SlugField(max_length=255, unique=True,
        help_text=ugettext_lazy("A very short name for this region that will appear in URLs, e.g. 'sf'. "
            "Keep it short and memorable!"))
    geom = models.MultiPolygonField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.slug)
        super(Region, self).save(*args, **kwargs)

    def populate_region(self, *args, **kwargs):
        from pages.models import Page
        from initial_data import populate_region

        if Page.objects.filter(region=self):
            raise IntegrityError(_("Region already has pages in it"))
        populate_region(self)

    def get_nearby_regions(self):
        # XXX CACHE
        if not self.geom:
            return
        center = self.geom.centroid
        rgs = Region.objects.exclude(geom__isnull=True).exclude(id=self.id).exclude(regionsettings__is_meta_region=True).exclude(is_active=False).distance(center).order_by('distance')
        # Return 6 nearest now. TODO: Rank by page count?
        return rgs[:6]

    def is_admin(self, user):
        """
        Is the provided `user` an admin of the region?
        """
        if not hasattr(self, 'regionsettings'):
            return False
        return self.regionsettings.admins.filter(id=user.id)

    def get_absolute_url(self):
        return reverse('frontpage', kwargs={'region': self.slug})


LANGUAGES = [(lang[0], ugettext_lazy(lang[1])) for lang in settings.LANGUAGES]

class RegionSettings(models.Model):
    region = models.OneToOneField(Region)

    # Can be null for meta regions, which may not have a geometry.
    region_center = models.PointField(null=True, blank=True)
    region_zoom_level = models.IntegerField(null=True, blank=True)

    admins = models.ManyToManyField(User, null=True)
    default_language = models.CharField(max_length=7, blank=True, null=True, choices=LANGUAGES)

    # Admin-only options
    domain = models.CharField(max_length=200, null=True)
    logo = models.ImageField("logo", upload_to="regions/logos/",
        storage=RandomFilenameFileSystemStorage(), null=True, blank=True)
    is_meta_region = models.BooleanField(default=False)

    def __unicode__(self):
        return 'settings: %s' % str(self.region)


class BannedFromRegion(models.Model):
    region = models.OneToOneField(Region)
    users = models.ManyToManyField(User, null=True)

    def __unicode__(self):
        return 'banned users on %s' % str(self.region)


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
