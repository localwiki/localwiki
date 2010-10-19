from django.db import models
import datetime

from trackchanges.models import TrackChanges

class Page(models.Model):
    name = models.CharField(max_length=200)
    body = models.TextField()

    history = TrackChanges()

    def __unicode__(self):
        return self.name

class FilePage(models.Model):
    name = models.CharField(max_length=200)
    body = models.TextField()
    file = models.FileField(upload_to='test_omg')

    def __unicode__(self):
        return self.name

class DateTest(models.Model):
    date = models.DateTimeField(default=datetime.datetime.now)
    name = models.CharField(max_length=200)
