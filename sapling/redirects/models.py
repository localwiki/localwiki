from django.db import models

from pages.models import Page


class Redirect(models.Model):
    source = models.SlugField(max_length=255, unique=True, editable=False)
    destination = models.ForeignKey(Page)

    def __unicode__(self):
        return "%s ---> %s" % (self.source, self.destination)
