# encoding: utf-8
from south.v2 import DataMigration
from django.contrib.contenttypes.management import update_contenttypes
from django.db.models.loading import get_app
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Permission


class Migration(DataMigration):

    def forwards(self, orm):
        contenttypes = orm['contenttypes.ContentType'].objects
        removed = set()
        for ct in contenttypes.filter(model__endswith='_hist')\
                              .exclude(name__endswith=' history'):
            removed.add(ct.app_label)
            Permission.objects.filter(content_type=ct).delete()
            ct.delete()
        for app_label in removed:
            app = get_app(app_label)
            update_contenttypes(app, None)
            create_permissions(app, None, 2)

    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['contenttypes', 'versioning']
