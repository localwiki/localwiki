import copy
import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from utils import *
from storage import *
from registry import *
import manager

class TrackChanges(object):
    def contribute_to_class(self, cls, name):
        self.manager_name = name
        models.signals.class_prepared.connect(self.finalize, sender=cls)

    def finalize(self, sender, **kwargs):
        history_model = self.create_history_model(sender)

        # The TrackChanges object will be discarded,
        # so the signal handlers can't use weak references.
        models.signals.post_save.connect(
            self.post_save, sender=sender, weak=False
        )
        models.signals.pre_delete.connect(
            self.pre_delete, sender=sender, weak=False
        )
        models.signals.post_delete.connect(
            self.post_delete, sender=sender, weak=False
        )

        self.wrap_model_fields(sender)

        descriptor = manager.HistoryDescriptor(history_model)
        setattr(sender, self.manager_name, descriptor)

    def create_history_model(self, model):
        """
        Creates a historical model to associate with the model provided.

        See http://code.djangoproject.com/wiki/DynamicModels
        Django 'sees' this new historical model class and actually creates a
        new model in the database (on syncdb) named <originalmodel>_history.
        This happens because the class that's returned is just like a normal
        model definition ('class MyModel(models.Model)') in the eyes of the
        Django machinery.

        @returns: Class representing the historical version of the model.
        """
        attrs = self.copy_fields(model)
        attrs.update(self.get_extra_fields(model))
        attrs.update(Meta=type('Meta', (), self.get_meta_options(model)))
        name = '%s_history' % model._meta.object_name
        return type(name, (models.Model,), attrs)

    def wrap_model_fields(self, model):
        """
        Wrap some
        """
        pass
        for field in model._meta.fields:
            if isinstance(field, models.FileField):
                field.storage = FileStorageWrapper(field.storage)

    def copy_fields(self, model):
        """
        Creates copies of the model's original fields, returning
        a dictionary mapping field name to copied field object.
        """
        # Though not strictly a field, this attribute
        # is required for a model to function properly.
        fields = {'__module__': model.__module__}

        for field in model._meta.fields:
            field = copy.copy(field)

            if isinstance(field, models.AutoField):
                # The historical model gets its own AutoField, so any
                # existing one must be replaced with an IntegerField.
                field.__class__ = models.IntegerField
                field.serialize = True

            if field.primary_key or field.unique:
                # Unique fields can no longer be guaranteed unique,
                # but they should still be indexed for faster lookups.
                field.primary_key = False
                field._unique = False
                field.db_index = True
            fields[field.name] = field

        return fields

    def get_extra_fields(self, model):
        """
        Returns a dictionary of fields that will be added to the historical
        record model, in addition to the ones returned by copy_fields below.

        If you subclass TrackChanges this is a good method to over-ride --
        simply add your own values to the fields for custom fields.
        """
        # XXX
        # TODO
        # Add AutoUserField here and make sure we can over-ride it
        # Similarly, make a AutoIPAddressField

        fields = {
            'history_id': models.AutoField(primary_key=True),
            'history_date': models.DateTimeField(default=datetime.datetime.now),
            'history_type': models.CharField(max_length=1, choices=(
                ('+', 'Created'),
                ('~', 'Changed'),
                ('-', 'Deleted'),
            )),
            'history_comment': models.CharField(max_length=200, blank=True,
                                                null=True
            ),
            'history_user': AutoUserField(null=True),
            'history_user_ip': AutoIPAddressField(null=True),
            'history_object': HistoricalObjectDescriptor(model),
            'history_get_version_number': version_number_of,
            '__unicode__': lambda self: u'%s as of %s' % (self.history_object,
                                                          self.history_date)
        }
        # lookup function for cleaniness. Instead of doing
        # h.history_ip_address we can write h.history_meta.ip_address
        fields['history_meta'] = HistoricalMetaInfo()

        return fields

    def get_meta_options(self, model):
        """
        Returns a dictionary of fields that will be added to
        the Meta inner class of the track changes model.
        """
        return {
            'ordering': ('-history_date',),
        }

    def post_save(self, instance, created, **kwargs):
        self.create_historical_record(instance, created and '+' or '~')

    def pre_delete(self, instance, **kwargs):
        self._pk_recycle_cleanup(instance)

    def post_delete(self, instance, **kwargs):
        if not self._is_pk_recycle_a_problem(instance):
            self.create_historical_record(instance, '-')

    def create_historical_record(self, instance, type):
        manager = getattr(instance, self.manager_name)
        # if they set track_changes to False
        # then we don't auto-create a revision here
        if not manager.track_changes:
            return
        attrs = {}
        for field in instance._meta.fields:
            attrs[field.attname] = getattr(instance, field.attname)
        attrs.update(manager._save_with)
        manager.create(history_type=type, **attrs)

    def _is_pk_recycle_a_problem(self, instance):
        manager = getattr(instance, self.manager_name)
        if (settings.DATABASE_ENGINE == 'sqlite3' and
            not manager._instance_unique_fields()):
            return True

    def _pk_recycle_cleanup(self, instance):
        """
        SQLite recycles autofield primary keys.  Oops!
        This will be fixed eventually:
        Django Ticket #10164: http://code.djangoproject.com/ticket/10164

        As a temporary consistency fix, we zero-out history of deleted objects
        that lack unique fields to prevent history-mystery!  The alternative
        would be to throw an error on deletion of these objects.
        """
        if not self._is_pk_recycle_a_problem(instance):
            return

        manager = getattr(instance, self.manager_name)
        for entry in manager.all():
            entry.delete()

class AutoUserField(models.ForeignKey):
    def __init__(self, **kws):
        super(AutoUserField, self).__init__(User, **kws)

    def contribute_to_class(self, cls, name):
        super(AutoUserField, self).contribute_to_class(cls, name)
        registry = FieldRegistry('user')
        registry.add_field(cls, self)

class AutoIPAddressField(models.IPAddressField):
    def contribute_to_class(self, cls, name):
        super(AutoIPAddressField, self).contribute_to_class(cls, name)
        registry = FieldRegistry('ip')
        registry.add_field(cls, self)
