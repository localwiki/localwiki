from django.db import models


class Redirect(models.Model):
    source = models.SlugField(max_length=255, unique=True)
    destination = models.SlugField(max_length=255)

    def __unicode__(self):
        return "%s ---> %s" % (self.source, self.destination)
