from django.db import models

from versionutils import versioning

"""
TODO: It would be cool to write a little thing to randomly generate
model definitions for tests.
"""


class M1(models.Model):
    a = models.CharField(max_length=200)
    b = models.CharField(max_length=200)
    c = models.CharField(max_length=200)
    d = models.CharField(max_length=200)

versioning.register(M1)


class M2(models.Model):
    a = models.CharField(max_length=200)
    b = models.TextField()
    c = models.IntegerField()

versioning.register(M2)


class M3BigInteger(models.Model):
    a = models.CharField(max_length=200)
    b = models.BooleanField(default=False)
    c = models.BigIntegerField()

versioning.register(M3BigInteger)


class M4Date(models.Model):
    a = models.DateTimeField(auto_now_add=True)
    b = models.DateField(auto_now_add=True)

versioning.register(M4Date)


class M5Decimal(models.Model):
    a = models.DecimalField(max_digits=19, decimal_places=3)
    b = models.DecimalField(max_digits=5, decimal_places=2)

versioning.register(M5Decimal)


class M6Email(models.Model):
    a = models.EmailField()

versioning.register(M6Email)


class M7Numbers(models.Model):
    a = models.FloatField()
    b = models.PositiveIntegerField()
    c = models.PositiveSmallIntegerField()
    d = models.SmallIntegerField()

versioning.register(M7Numbers)


class M8Time(models.Model):
    a = models.TimeField(auto_now_add=True)

versioning.register(M8Time)


class M9URL(models.Model):
    a = models.URLField(verify_exists=False)

versioning.register(M9URL)


class M10File(models.Model):
    a = models.FileField(upload_to='test_versioning_uploads')

versioning.register(M10File)


class M11Image(models.Model):
    a = models.ImageField(upload_to='test_versioning_uploads')

versioning.register(M11Image)


class M12ForeignKey(models.Model):
    a = models.ForeignKey(M2)
    b = models.CharField(max_length=200)

versioning.register(M12ForeignKey)


class M12ForeignKeysRelatedSpecified(models.Model):
    a = models.ForeignKey(M2, related_name="g")
    b = models.CharField(max_length=200)

versioning.register(M12ForeignKeysRelatedSpecified)


class M13ForeignKeySelf(models.Model):
    a = models.ForeignKey('self', null=True)
    b = models.CharField(max_length=200)

versioning.register(M13ForeignKeySelf)


class Category(models.Model):
    a = models.CharField(max_length=200)


class M14ManyToMany(models.Model):
    a = models.TextField()
    b = models.ManyToManyField(Category)

versioning.register(M14ManyToMany)


class LongerNameOfThing(models.Model):
    a = models.TextField()

versioning.register(LongerNameOfThing)


class M15OneToOne(models.Model):
    a = models.CharField(max_length=200)
    b = models.OneToOneField(LongerNameOfThing)

versioning.register(M15OneToOne)


class M16Unique(models.Model):
    a = models.CharField(max_length=200, unique=True)
    b = models.TextField()
    c = models.IntegerField()

versioning.register(M16Unique)


class M17ForeignKeyVersioned(models.Model):
    name = models.CharField(max_length=200)
    m2 = models.ForeignKey(M2)

versioning.register(M17ForeignKeyVersioned)


class M17ForeignKeyVersionedCustom(models.Model):
    name = models.CharField(max_length=200)
    m2 = models.ForeignKey(M2)

versioning.register(M17ForeignKeyVersionedCustom)


class M18OneToOneFieldVersioned(models.Model):
    name = models.CharField(max_length=200)
    m2 = models.OneToOneField(M2)

versioning.register(M18OneToOneFieldVersioned)


class LameTag(models.Model):
    name = models.CharField(max_length=200)

versioning.register(LameTag)


class M19ManyToManyFieldVersioned(models.Model):
    a = models.TextField()
    tags = models.ManyToManyField(LameTag)

versioning.register(M19ManyToManyFieldVersioned)


class CustomManager(models.Manager):
    def foo(self):
        return "bar"


class M20CustomManager(models.Model):
    name = models.CharField(max_length=200)
    objects = models.Manager()

    myman = CustomManager()

versioning.register(M20CustomManager)


class M20CustomManagerDirect(models.Model):
    name = models.CharField(max_length=200)
    objects = CustomManager()

versioning.register(M20CustomManagerDirect)


class M21CustomAttribute(models.Model):
    name = models.CharField(max_length=200)
    magic = "YES"

versioning.register(M21CustomAttribute)


class M21CustomMethod(models.Model):
    name = models.CharField(max_length=200)

    def myfunc(self):
        return self.name

versioning.register(M21CustomMethod)


class M22ManyToManySelfVersioned(models.Model):
    a = models.TextField()
    tags = models.ManyToManyField('self')

versioning.register(M22ManyToManySelfVersioned)


class M23AutoNow(models.Model):
    a = models.DateTimeField(auto_now=True)
    b = models.CharField(max_length=200)

versioning.register(M23AutoNow)


class MUniqueAndFK(models.Model):
    a = models.CharField(max_length=200, unique=True)
    b = models.CharField(max_length=200)
    c = models.ForeignKey(M16Unique)

versioning.register(MUniqueAndFK)


class MUniqueAndFK2(models.Model):
    a = models.CharField(max_length=200, unique=True)
    b = models.CharField(max_length=200)
    c = models.ForeignKey(MUniqueAndFK)

versioning.register(MUniqueAndFK2)

############################################################
# Model inheritance test models
############################################################


class M24ProxyModel(models.Model):
    a = models.CharField(max_length=100)

versioning.register(M24ProxyModel)


class M24SubclassProxy(M24ProxyModel):
    def myfunc(self):
        return True

    class Meta:
        proxy = True


class M25AbstractModel(models.Model):
    a = models.CharField(max_length=100)

    class Meta:
        abstract = True


class M25SubclassAbstract(M25AbstractModel):
    b = models.CharField(max_length=100)

versioning.register(M25SubclassAbstract)

# Concrete model inheritence
# --------------------------


class M26ConcreteModelA(models.Model):
    a = models.CharField(max_length=100)


class M26SubclassConcreteA(M26ConcreteModelA):
    b = models.CharField(max_length=100)

versioning.register(M26SubclassConcreteA)


class M26ConcreteModelB(models.Model):
    a = models.CharField(max_length=100)

versioning.register(M26ConcreteModelB)


class M26SubclassConcreteB(M26ConcreteModelB):
    b = models.CharField(max_length=100)


class M26ConcreteModelC(models.Model):
    a = models.CharField(max_length=100)

versioning.register(M26ConcreteModelC)


class M26SubclassConcreteC(M26ConcreteModelC):
    b = models.CharField(max_length=100)

versioning.register(M26SubclassConcreteC)


class NonVersionedModel(models.Model):
    a = models.CharField(max_length=100)


TEST_MODELS = [
    M1, M2, M3BigInteger, M4Date, M5Decimal, M6Email, M7Numbers,
    M8Time, M9URL, M10File, M11Image, M12ForeignKey, M13ForeignKeySelf,
    M14ManyToMany, M15OneToOne, M16Unique, M17ForeignKeyVersioned,
    M18OneToOneFieldVersioned, M19ManyToManyFieldVersioned,
    M20CustomManager, M21CustomAttribute,
    M22ManyToManySelfVersioned, M23AutoNow,
    M24SubclassProxy, M25SubclassAbstract,
    M26SubclassConcreteA, M26ConcreteModelB,
    M26SubclassConcreteB, M26ConcreteModelC, M26SubclassConcreteC,
    MUniqueAndFK, MUniqueAndFK2,
    NonVersionedModel,
]
