# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Region'
        db.create_table('regions_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(null=True, blank=True)),
        ))
        db.send_create_signal('regions', ['Region'])

        # Adding model 'RegionSettings'
        db.create_table('regions_regionsettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('region', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['regions.Region'], unique=True)),
            ('region_center', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('region_zoom_level', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('regions', ['RegionSettings'])


    def backwards(self, orm):
        # Deleting model 'Region'
        db.delete_table('regions_region')

        # Deleting model 'RegionSettings'
        db.delete_table('regions_regionsettings')


    models = {
        'regions.region': {
            'Meta': {'object_name': 'Region'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'})
        },
        'regions.regionsettings': {
            'Meta': {'object_name': 'RegionSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['regions.Region']", 'unique': 'True'}),
            'region_center': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'region_zoom_level': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['regions']