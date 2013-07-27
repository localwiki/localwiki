# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tag'
        db.create_table('tags_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('tags', ['Tag'])

        # Adding model 'Tag_hist'
        db.create_table('tags_tag_hist', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('history_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('history_type', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('history_reverted_to_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tags.Tag_hist'], null=True)),
            ('history_comment', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('history_user', self.gf('versionutils.versioning.fields.AutoUserField')(to=orm['auth.User'], null=True)),
            ('history_user_ip', self.gf('versionutils.versioning.fields.AutoIPAddressField')(max_length=15, null=True)),
        ))
        db.send_create_signal('tags', ['Tag_hist'])

        # Adding model 'PageTagSet'
        db.create_table('tags_pagetagset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True)),
        ))
        db.send_create_signal('tags', ['PageTagSet'])

        # Adding M2M table for field tags on 'PageTagSet'
        db.create_table('tags_pagetagset_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pagetagset', models.ForeignKey(orm['tags.pagetagset'], null=False)),
            ('tag', models.ForeignKey(orm['tags.tag'], null=False))
        ))
        db.create_unique('tags_pagetagset_tags', ['pagetagset_id', 'tag_id'])

        # Adding model 'PageTagSet_hist'
        db.create_table('tags_pagetagset_hist', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('history_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('history_type', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('history_reverted_to_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tags.PageTagSet_hist'], null=True)),
            ('history_comment', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('history_user', self.gf('versionutils.versioning.fields.AutoUserField')(to=orm['auth.User'], null=True)),
            ('history_user_ip', self.gf('versionutils.versioning.fields.AutoIPAddressField')(max_length=15, null=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Page_hist'])),
        ))
        db.send_create_signal('tags', ['PageTagSet_hist'])

        # Adding M2M table for field tags on 'PageTagSet_hist'
        db.create_table('tags_pagetagset_hist_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pagetagset_hist', models.ForeignKey(orm['tags.pagetagset_hist'], null=False)),
            ('tag_hist', models.ForeignKey(orm['tags.tag_hist'], null=False))
        ))
        db.create_unique('tags_pagetagset_hist_tags', ['pagetagset_hist_id', 'tag_hist_id'])

    def backwards(self, orm):
        # Deleting model 'Tag'
        db.delete_table('tags_tag')

        # Deleting model 'Tag_hist'
        db.delete_table('tags_tag_hist')

        # Deleting model 'PageTagSet'
        db.delete_table('tags_pagetagset')

        # Removing M2M table for field tags on 'PageTagSet'
        db.delete_table('tags_pagetagset_tags')

        # Deleting model 'PageTagSet_hist'
        db.delete_table('tags_pagetagset_hist')

        # Removing M2M table for field tags on 'PageTagSet_hist'
        db.delete_table('tags_pagetagset_hist_tags')

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
        },
        'tags.pagetagset': {
            'Meta': {'ordering': "('page__slug',)", 'object_name': 'PageTagSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True'}),
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
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tags.Tag_hist']", 'symmetrical': 'False'})
        },
        'tags.tag': {
            'Meta': {'ordering': "('slug',)", 'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
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
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        }
    }

    complete_apps = ['tags']