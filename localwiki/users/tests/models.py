from django.db import models
from django.db.models.fields import CharField


class Thing(models.Model):
    name = CharField(max_length=30)
