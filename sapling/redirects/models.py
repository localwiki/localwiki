from django.utils.translation import ugettext as _
from django.db import models
from django.db.models.signals import pre_save
from django.core.urlresolvers import reverse

from pages.models import Page
from versionutils import versioning

import exceptions


class Redirect(models.Model):
    source = models.SlugField(max_length=255, unique=True, editable=False)
    destination = models.ForeignKey(Page)

    def __unicode__(self):
        return "%s ---> %s" % (self.source, self.destination)

    def get_absolute_url(self):
        return reverse('pages:show', args=[self.source])


versioning.register(Redirect)


def _validate_redirect(sender, instance, raw, **kws):
    if instance.source == instance.destination.slug:
            raise exceptions.RedirectToSelf(
                    _("You cannot redirect a page to itself"))

pre_save.connect(_validate_redirect, sender=Redirect)

# For registration calls
import feeds
import api
