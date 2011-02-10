from django.db import models
import datetime

from trackchanges.models import TrackChanges

class Page(models.Model):
    name = models.CharField(max_length=200, unique=True)
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

class Tag(models.Model):
    name = models.CharField(max_length=200)

    history = TrackChanges()

class FK(models.Model):
    a = models.CharField(max_length=200)
    b = models.ForeignKey(Tag, null=True)

    history = TrackChanges()

class TagNoVer(models.Model):
    name = models.CharField(max_length=200)

class FKNoVer(models.Model):
    a = models.CharField(max_length=200)
    b = models.ForeignKey(TagNoVer, null=True)

    history = TrackChanges()

class FKM(models.Model):
    a = models.CharField(max_length=200)
    b = models.ManyToManyField(Tag, null=True)

    history = TrackChanges()

class OneToOne(models.Model):
    a = models.CharField(max_length=200)
    b = models.OneToOneField(Page)

    history = TrackChanges()

class OneToOneNotVersioned(models.Model):
    a = models.CharField(max_length=200)
    b = models.OneToOneField(Page)

class Person(models.Model):
    name = models.CharField(max_length=200)

class AnotherPage(models.Model):
    name = models.CharField(max_length=200, unique=True)
    body = models.TextField()
    person = models.ForeignKey(Person)

class YetAnotherPage(models.Model):
    name = models.CharField(max_length=200, unique=True)
    body = models.TextField()
    person = models.ForeignKey(Person, related_name="otherpages")

class NoFKConstraint(models.Model):
    name = models.CharField(max_length=200)
    tag = models.ForeignKey(Tag)

class FKToSelf(models.Model):
    a = models.CharField(max_length=200)
    b = models.ForeignKey('self', null=True)

    history = TrackChanges()

#class M2(models.Model):
#    a = models.CharField(max_length=200)
#    b = models.TextField()
#    c = models.IntegerField()
#
#    history = TrackChanges()
#
#class M12ForeignKey(models.Model):
#    a = models.ForeignKey(M2)
#    b = models.CharField(max_length=200)
#
#    history = TrackChanges()


#from page.models import *
#
#t = Tag(name="alphaandomega6")
#t.save()
#
#fk = FK(a="needfood6", b=t)
#fk.save()
#
#
