from django.db import models
from django.utils.translation import ugettext_lazy

from django_randomfilenamestorage.storage import (
    RandomFilenameFileSystemStorage)

from regions.models import Region


class FrontPage(models.Model):
    cover_photo = models.ImageField("cover_photo", upload_to="frontpage/files/",
        storage=RandomFilenameFileSystemStorage(), null=True)
    cover_photo_full = models.ImageField("cover_photo_full", upload_to="frontpage/files/",
        storage=RandomFilenameFileSystemStorage(), null=True)
    cover_photo_crop_bbox_left = models.IntegerField(null=True)
    cover_photo_crop_bbox_upper = models.IntegerField(null=True)
    cover_photo_crop_bbox_right = models.IntegerField(null=True)
    cover_photo_crop_bbox_lower = models.IntegerField(null=True)

    region = models.ForeignKey(Region)
