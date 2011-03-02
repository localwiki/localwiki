from django.db import models

from versionutils import diff
from versionutils.versioning import TrackChanges

"""
TODO: It would be cool to write a little thing to randomly generate
model definitions for tests.
"""


class M1(models.Model):
    a = models.CharField(max_length=200)
    b = models.TextField()
    c = models.DateTimeField()
    d = models.IntegerField()


class M1Diff(diff.BaseModelDiff):
    fields = ('d', 'c', 'b', 'a',)


class M1FieldDiff(diff.BaseFieldDiff):
    pass


class M2(models.Model):
    a = models.FileField(upload_to='test_diff_uploads')


class M3(models.Model):
    a = models.ImageField(upload_to='test_diff_uploads')


class M4ForeignKey(models.Model):
    a = models.ForeignKey('M1')

class M5Versioned(models.Model):
    a = models.CharField(max_length=200)

    history = TrackChanges()

#class M3BigInteger(models.Model):
#    a = models.CharField(max_length=200)
#    b = models.BooleanField(default=False)
#    c = models.BigIntegerField()
#
#class M4Date(models.Model):
#    a = models.DateTimeField(auto_now_add=True)
#    b = models.DateField(auto_now_add=True)
#
#class M5Decimal(models.Model):
#    a = models.DecimalField(max_digits=19, decimal_places=3)
#    b = models.DecimalField(max_digits=5, decimal_places=2)
#
#class M6Email(models.Model):
#    a = models.EmailField()
#
#class M7Numbers(models.Model):
#    a = models.FloatField()
#    b = models.PositiveIntegerField()
#    c = models.PositiveSmallIntegerField()
#    d = models.SmallIntegerField()
#
#class M8Time(models.Model):
#    a = models.TimeField(auto_now_add=True)
#
#class M9URL(models.Model):
#    a = models.URLField(verify_exists=False)
#
#class M10File(models.Model):
#    a = models.FileField(upload_to='test_trackchanges_uploads')
#
#class M11Image(models.Model):
#    a = models.ImageField(upload_to='test_trackchanges_uploads')
#
#class M12ForeignKeys(models.Model):
#    a = models.ForeignKey(M1)
#    b = models.CharField(max_length=200)
#
#class M13ForeignKeySelf(models.Model):
#    a = models.ForeignKey('self', null=True)
#    b = models.CharField(max_length=200)
#
#class Category(models.Model):
#    a = models.CharField(max_length=200)
#
#class M14ManyToMany(models.Model):
#    a = models.TextField()
#    b = models.ManyToManyField(Category)
#
#class LongerNameOfThing(models.Model):
#    a = models.TextField()
#
#class M15OneToOne(models.Model):
#    a = models.CharField(max_length=200)
#    b = models.OneToOneField(LongerNameOfThing)
#
#class M16Unique(models.Model):
#    a = models.CharField(max_length=200, unique=True)
#    b = models.TextField()
#    c = models.IntegerField()

TEST_MODELS = [
    M1, M2, 
]
