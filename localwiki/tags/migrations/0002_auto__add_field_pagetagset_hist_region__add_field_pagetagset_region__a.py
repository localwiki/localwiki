# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Tag', fields ['slug']
        db.delete_unique('tags_tag', ['slug'])

        # Adding field 'PageTagSet_hist.region'
        db.add_column('tags_pagetagset_hist', 'region',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['regions.Region'], null=True),
                      keep_default=False)

        # Adding field 'PageTagSet.region'
        db.add_column('tags_pagetagset', 'region',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['regions.Region'], null=True),
                      keep_default=False)

        # Adding field 'Tag_hist.region'
        db.add_column('tags_tag_hist', 'region',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['regions.Region'], null=True),
                      keep_default=False)

        # Removing index on 'Tag_hist', fields ['slug']
        db.delete_index('tags_tag_hist', ['slug'])

        # Adding field 'Tag.region'
        db.add_column('tags_tag', 'region',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['regions.Region'], null=True),
                      keep_default=False)

        # Adding unique constraint on 'Tag', fields ['slug', 'region']
        db.create_unique('tags_tag', ['slug', 'region_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Tag', fields ['slug', 'region']
        db.delete_unique('tags_tag', ['slug', 'region_id'])

        # Adding index on 'Tag_hist', fields ['slug']
        db.create_index('tags_tag_hist', ['slug'])

        # Deleting field 'PageTagSet_hist.region'
        db.delete_column('tags_pagetagset_hist', 'region_id')

        # Deleting field 'PageTagSet.region'
        db.delete_column('tags_pagetagset', 'region_id')

        # Deleting field 'Tag_hist.region'
        db.delete_column('tags_tag_hist', 'region_id')

        # Deleting field 'Tag.region'
        db.delete_column('tags_tag', 'region_id')

        # Adding unique constraint on 'Tag', fields ['slug']
        db.create_unique('tags_tag', ['slug'])


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
        'pages.page': {
            'Meta': {'unique_together': "(('slug', 'region'),)", 'object_name': 'Page'},
            'content': ('pages.fields.WikiHTMLField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['regions.Region']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'})
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
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['regions.Region']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'})
        },
        'regions.region': {
            'Meta': {'object_name': 'Region'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'})
        },
        'tags.pagetagset': {
            'Meta': {'ordering': "('page__slug',)", 'object_name': 'PageTagSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['regions.Region']", 'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tags.Tag']", 'symmetrical': 'False'})
        },
        'tags.pagetagset_hist': {
            'Meta': {'ordering': "('-history_date',)", 'object_name': 'PageTagSet_hist'},
            'history_comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'history_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'history_reverted_to_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tags.PageTagSet_hist']", 'null': 'True'}),
            'history_type': ('django.db.models.fields.SmallIntegerField', [], {}),
            'history_user': ('versionutils.versioning.fields.AutoUserField', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'history_user_ip': ('versionutils.versioning.fields.AutoIPAddressField', [], {'max_length': '15', 'null': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pages.Page_hist']"}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['regions.Region']", 'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tags.Tag_hist']", 'symmetrical': 'False'})
        },
        'tags.tag': {
            'Meta': {'ordering': "('slug',)", 'unique_together': "(('slug', 'region'),)", 'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['regions.Region']", 'null': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tags.tag_hist': {
            'Meta': {'ordering': "('-history_date',)", 'object_name': 'Tag_hist'},
            'history_comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'history_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'history_reverted_to_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tags.Tag_hist']", 'null': 'True'}),
            'history_type': ('django.db.models.fields.SmallIntegerField', [], {}),
            'history_user': ('versionutils.versioning.fields.AutoUserField', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'history_user_ip': ('versionutils.versioning.fields.AutoIPAddressField', [], {'max_length': '15', 'null': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['regions.Region']", 'null': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['tags']