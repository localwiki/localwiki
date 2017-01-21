from django.db import models

from versionutils import diff
from versionutils import versioning


class Diff_M1(models.Model):
    a = models.CharField(max_length=200)
    b = models.TextField()
    c = models.DateTimeField()
    d = models.IntegerField()


class Diff_M1Diff(diff.BaseModelDiff):
    fields = ('d', 'c', 'b', 'a',)


class Diff_M1FieldDiff(diff.BaseFieldDiff):
    pass


class Diff_M2(models.Model):
    a = models.FileField(upload_to='test_diff_uploads')


class Diff_M3(models.Model):
    a = models.ImageField(upload_to='test_diff_uploads')


class Diff_M4ForeignKey(models.Model):
    a = models.ForeignKey('Diff_M1')


class Diff_M5Versioned(models.Model):
    a = models.CharField(max_length=200)

versioning.register(Diff_M5Versioned)


class FakeFieldModel(models.Model):
    a = models.CharField(max_length=200)

    def b(self):
        return 'a is ' + self.a
    b = property(b)


class FakeFieldModelDiff(diff.BaseModelDiff):
    fields = (('b', diff.TextFieldDiff),)


TEST_MODELS = [
    Diff_M1, Diff_M2
]
