from django.db import models

from versionutils.versioning import TrackChanges

class Person(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    history = TrackChanges()

class Profile(models.Model):
    details = models.TextField()
    person = models.ForeignKey(Person)

    history = TrackChanges()

class AutoNow(models.Model):
    last_modified = models.DateTimeField(auto_now=True)
    description = models.TextField()

class Handle(models.Model):
    name = models.CharField(max_length=200)
    person = models.OneToOneField(Person)

    history = TrackChanges()
