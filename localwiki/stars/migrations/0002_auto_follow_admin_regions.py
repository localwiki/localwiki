# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from follow.models import Follow

from regions.models import RegionSettings


class Migration(DataMigration):

    def forwards(self, orm):
        for rs in RegionSettings.objects.all():
            for u in rs.admins.all():
                if not Follow.objects.filter(user=u, target_region=rs.region):
                    Follow(user=u, target_region=rs.region).save()

    def backwards(self, orm):
        pass

    models = {
        
    }

    complete_apps = ['stars']
    symmetrical = True
