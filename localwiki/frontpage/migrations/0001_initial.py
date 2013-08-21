# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FrontPage'
        db.create_table('frontpage_frontpage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cover_photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['regions.Region'])),
        ))
        db.send_create_signal('frontpage', ['FrontPage'])


    def backwards(self, orm):
        # Deleting model 'FrontPage'
        db.delete_table('frontpage_frontpage')


    models = {
        'frontpage.frontpage': {
            'Meta': {'object_name': 'FrontPage'},
            'cover_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['regions.Region']"})
        },
        'regions.region': {
            'Meta': {'object_name': 'Region'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['frontpage']