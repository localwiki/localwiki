import copy
import datetime
from functools import partial

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from utils import *
from storage import *
from registry import *
from constants import *
import manager

class TrackChanges(object):
    def contribute_to_class(self, cls, name):
        self.manager_name = name
        models.signals.class_prepared.connect(self.finalize, sender=cls)

    def finalize(self, sender, **kwargs):
        history_model = self.create_history_model(sender)

        setattr(sender, '_track_changes', True)

        # Over-ride the save, delete methods to allow arguments to be passed in
        # such as comment="Made a small change."
        setattr(sender, 'save', save_with_arguments)
        setattr(sender, 'delete', delete_with_arguments)

        # We also attach signal handlers to the save, delete methods.  It's
        # easier to have two things going on (signal, and an overridden method)
        # because the signal handlers tell us if the object is new or not.
        # (Just checking object.pk is None is not enough!)

        # The TrackChanges object will be discarded, so the signal handlers
        # can't use weak references.
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
        # being able to look this up is intensely helpful
        setattr(sender, '_history_manager_name', self.manager_name)

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
        attrs.update(self._get_history_fields(model))
        attrs.update(self.get_extra_history_fields(model))
        attrs.update(Meta=type('Meta', (), self.get_meta_options(model)))
        name = '%s_history' % model._meta.object_name
        return type(name, (models.Model,), attrs)

    def wrap_model_fields(self, model):
        """
        Wrap some of the model's fields to add extra behavior.
        """
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

    def get_extra_history_fields(self, model):
        """
        Returns a dictionary of the non-essential fields that will be added to
        the historical record model.

        If you subclass TrackChanges this is a good method to over-ride --
        simply add your own values to the fields for custom fields.

        NOTE: Your custom fields should start with history_ if you want them to
              be looked up via hm.history_info.fieldname
        """
        fields = {
            'history_comment': models.CharField(max_length=200, blank=True,
                                                null=True
            ),
            'history_user': AutoUserField(null=True),
            'history_user_ip': AutoIPAddressField(null=True),
            '__unicode__': lambda self: u'%s as of %s' % (self.history__object,
                                                          self.history_date)
        }

        return fields

    def _get_history_fields(self, model):
        """
        Returns a dictionary of the essential fields that will be added to the
        historical record model, in addition to the ones returned by copy_fields.
        """
        fields = {
            'history_id': models.AutoField(primary_key=True),
            'history__object': HistoricalObjectDescriptor(model),
            'history_date': models.DateTimeField(default=datetime.datetime.now),
            'history_version_number': version_number_of,
            'history_type': models.SmallIntegerField(choices=TYPE_CHOICES),
            # If you want to display "Reverted to version N" in every change
            # comment then you should stash that in the comment field
            # directly rather than using
            # reverted_to_version.version_number() on each display.
            'history_reverted_to_version': models.ForeignKey('self', null=True),
            # lookup function for cleaniness. Instead of doing
            # h.history_ip_address we can write h.history_info.ip_address
            'history_info': HistoricalMetaInfo(),
            'revert_to': revert_to,
            'save': save_with_arguments,
            'delete': delete_with_arguments,
            '__init__': historical_record_init,
            '__getattribute__':
                # not sure why functools.partial doesn't work here
                lambda m, name: historical_record_getattribute(model, m, name),
        }

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
        history_type = getattr(instance, '_history_type', None)
        is_revert = history_type == TYPE_REVERTED
        if created:
            history_type = TYPE_REVERTED_ADDED if is_revert else TYPE_ADDED
        else:
            history_type = history_type or TYPE_UPDATED
        self.create_historical_record(instance, history_type)

    def pre_delete(self, instance, **kwargs):
        self._pk_recycle_cleanup(instance)

    def post_delete(self, instance, **kwargs):
        history_type = getattr(instance, '_history_type', None)
        is_revert = history_type == TYPE_REVERTED
        history_type = TYPE_REVERTED_DELETED if is_revert else TYPE_DELETED
        if not self._is_pk_recycle_a_problem(instance):
            self.create_historical_record(instance, history_type)

    def create_historical_record(self, instance, type):
        manager = getattr(instance, self.manager_name)
        # if they set track_changes to False
        # then we don't auto-create a revision here
        if not instance._track_changes:
            return
        attrs = {}
        for field in instance._meta.fields:
            attrs[field.attname] = getattr(instance, field.attname)
        attrs.update(self._get_save_with_attrs(instance))
        manager.create(history_type=type, **attrs)

    def _get_save_with_attrs(self, instance):
        """
        Prefix all keys with 'history_' to save them into the history
        model correctly.
        """
        d = {}
        for k, v in getattr(instance, '_save_with', {}).iteritems():
            d['history_%s' % k] = v
        return d

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
