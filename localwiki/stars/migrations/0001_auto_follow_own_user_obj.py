# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.contrib.auth.models import User

from follow.models import Follow


class Migration(DataMigration):

    def forwards(self, orm):
        for u in User.objects.all():
            if not Follow.objects.filter(user=u, target_user=u):
                Follow(user=u, target_user=u).save()

    def backwards(self, orm):
        pass

    models = {
        
    }

    depends_on = (
        ("actstream", "0007_auto__add_field_follow_started"),
    )
    complete_apps = ['stars']
    symmetrical = True
