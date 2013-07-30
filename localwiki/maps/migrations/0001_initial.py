# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MapData'
        db.create_table('maps_mapdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('points', self.gf('django.contrib.gis.db.models.fields.MultiPointField')(null=True, blank=True)),
            ('lines', self.gf('django.contrib.gis.db.models.fields.MultiLineStringField')(null=True, blank=True)),
            ('polys', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(null=True, blank=True)),
            ('geom', self.gf('maps.fields.FlatCollectionFrom')(null=True)),
            ('length', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('page', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True)),
        ))
        db.send_create_signal('maps', ['MapData'])

        # Adding model 'MapData_hist'
        db.create_table('maps_mapdata_hist', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('points', self.gf('django.contrib.gis.db.models.fields.MultiPointField')(null=True, blank=True)),
            ('lines', self.gf('django.contrib.gis.db.models.fields.MultiLineStringField')(null=True, blank=True)),
            ('polys', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(null=True, blank=True)),
            ('geom', self.gf('maps.fields.FlatCollectionFrom')(null=True)),
            ('length', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('history_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('history_type', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('history_reverted_to_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maps.MapData_hist'], null=True)),
            ('history_comment', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('history_user', self.gf('versionutils.versioning.fields.AutoUserField')(to=orm['auth.User'], null=True)),
            ('history_user_ip', self.gf('versionutils.versioning.fields.AutoIPAddressField')(max_length=15, null=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Page_hist'])),
        ))
        db.send_create_signal('maps', ['MapData_hist'])

    def backwards(self, orm):
        # Deleting model 'MapData'
        db.delete_table('maps_mapdata')

        # Deleting model 'MapData_hist'
        db.delete_table('maps_mapdata_hist')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'maps.mapdata': {
            'Meta': {'object_name': 'MapData'},
            'geom': ('maps.fields.FlatCollectionFrom', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'lines': ('django.contrib.gis.db.models.fields.MultiLineStringField', [], {'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True'}),
            'points': ('django.contrib.gis.db.models.fields.MultiPointField', [], {'null': 'True', 'blank': 'True'}),
            'polys': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'})
        },
        'maps.mapdata_hist': {
            'Meta': {'ordering': "('-history_date',)", 'object_name': 'MapData_hist'},
            'geom': ('maps.fields.FlatCollectionFrom', [], {'null': 'True'}),
            'history_comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'history_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'history_reverted_to_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maps.MapData_hist']", 'null': 'True'}),
            'history_type': ('django.db.models.fields.SmallIntegerField', [], {}),
            'history_user': ('versionutils.versioning.fields.AutoUserField', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'history_user_ip': ('versionutils.versioning.fields.AutoIPAddressField', [], {'max_length': '15', 'null': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'lines': ('django.contrib.gis.db.models.fields.MultiLineStringField', [], {'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pages.Page_hist']"}),
            'points': ('django.contrib.gis.db.models.fields.MultiPointField', [], {'null': 'True', 'blank': 'True'}),
            'polys': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'})
        },
        'pages.page': {
            'Meta': {'object_name': 'Page'},
            'content': ('pages.fields.WikiHTMLField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'})
        },
        'pages.page_hist': {
            'Meta': {'ordering': "('-history_date',)", 'object_name': 'Page_hist'},
            'content': ('pages.fields.WikiHTMLField', [], {}),
            'history_comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'history_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'history_reverted_to_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pages.Page_hist']", 'null': 'True'}),
            'history_type': ('django.db.models.fields.SmallIntegerField', [], {}),
            'history_user': ('versionutils.versioning.fields.AutoUserField', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'history_user_ip': ('versionutils.versioning.fields.AutoIPAddressField', [], {'max_length': '15', 'null': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['maps']