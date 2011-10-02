from django.db import models

from pages.models import Page
from versionutils import versioning


class Redirect(models.Model):
    source = models.SlugField(max_length=255, unique=True, editable=False)
    destination = models.ForeignKey(Page)

    def __unicode__(self):
        return "%s ---> %s" % (self.source, self.destination)

versioning.register(Redirect)

import feeds # To fire register() calls.
