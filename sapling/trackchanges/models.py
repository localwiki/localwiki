import copy

from django.db import models
from django.conf import settings
from django.db.models.options import DEFAULT_NAMES as ALL_META_OPTIONS
from django.contrib.auth.models import User

from utils import *
from storage import *
from registry import *
from constants import *
from fields import *
from history_model_methods import get_history_fields
import manager

class TrackChanges(object):
    def contribute_to_class(self, cls, name):
        self.manager_name = name
        models.signals.class_prepared.connect(self.finalize, sender=cls)

    def finalize(self, sender, **kws):
        if self.ineligible_for_history_model(sender):
            return
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
        # Signal handlers are called when a bulk QuerySet.delete()
        # is issued -- custom delete() and save() methods aren't called
        # in that case.

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
        # Being able to look this up is intensely helpful.
        setattr(sender, '_history_manager_name', self.manager_name)

    def ineligible_for_history_model(self, model):
        """
        Certain abstract-y models can't have corresponding history models.
        """
        return model._meta.proxy or model._meta.abstract

    def create_history_model(self, model):
        """
        Creates a historical model to associate with the model provided.

        See http://code.djangoproject.com/wiki/DynamicModels
        Django 'sees' this new historical model class and actually creates a
        new model in the database (on syncdb) named <originalmodel>_hist.
        This happens because the class that's returned is just like a normal
        model definition ('class MyModel(models.Model)') in the eyes of the
        Django machinery.

        @returns: Class representing the historical version of the model.
        """
        attrs = self.get_misc_members(model)
        attrs.update(self.get_fields(model))
        attrs.update(get_history_fields(self, model))
        attrs.update(self.get_extra_history_fields(model))
        attrs.update(Meta=type('Meta', (), self.get_meta_options(model)))

        # For convience's sake, it's nice to be able to reference the
        # non-historical class from the historical class.
        attrs['_original_model'] = model

        name = '%s_hist' % model._meta.object_name
        return type(name, (models.Model,), attrs)

    def wrap_model_fields(self, model):
        """
        Wrap some of the model's fields to add extra behavior.
        """
        for field in model._meta.fields:
            if isinstance(field, models.FileField):
                field.storage = FileStorageWrapper(field.storage)

    MEMBERS_TO_SKIP = [
        '__dict__',
        '__module__',
        '__weakref__',
        # TODO, maybe: if we wanted to be fancy we could define our
        # own __doc__ that explains "this is like the normal model
        # plus these historical methods."
        '__doc__',
        '_meta',
        '_base_manager',
        '_default_manager',
    ]

    FK_FIELDS_TO_COPY = [
        'null',
        'blank',
        'db_index',
        'db_tablespace',
        'to_field'
    ]

    def get_misc_members(self, model):
        # Would like to know a better way to do this.
        # Ideally we would subclass the model and then extend it.
        # But Django won't let us replace a field (in our case, a
        # ForeignKey field we are replacing with a wrapped IntegerField)
        # Based on a message on twitter from Adrian, approaches like
        # http://bit.ly/gPXlgk to get around the subclass limitation
        # are a bad idea, but not sure why (?)
        d = copy.copy(dict(model.__dict__))
        for k in TrackChanges.MEMBERS_TO_SKIP:
            if d.get(k, None) is not None:
                del d[k]
        # Remove some fields we know we'll re-add in modified form
        # later.
        for k in d:
            if isinstance(d[k], models.fields.Field): del d[k]
        return d

    def get_fields(self, model):
        """
        Creates copies of the model's original fields, returning
        a dictionary mapping field name to copied field object.
        """
        #def _get_m2m_opts(field):
        #    field.
        # Though not strictly a field, this attribute
        # is required for a model to function properly.
        def _get_fk_opts(field):
            opts = {}
            for k in TrackChanges.FK_FIELDS_TO_COPY:
                if hasattr(field, k):
                    opts[k] = getattr(field, k, None)
            return opts
        fields = {'__module__': model.__module__}

        for field in (model._meta.fields + model._meta.many_to_many):
            field = copy.deepcopy(field)

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

            # page.fktoself_hist: Accessor for field 'b' clashes with related field 'FKToSelf_hist.fktoself_hist_set'. Add a related_name argument to the definition for 'b'.

            if isinstance(field, models.ForeignKey):
                is_fk_to_self = field.related.parent_model == model
                if is_fk_to_self:
                    options = _get_fk_opts(field)
                    # Fix related name conflict. We set this manually
                    # elsewhere so giving this a funky name isn't a
                    # problem.
                    options['related_name'] = '%s_hist_set_2' % field.related.var_name

                    hist_field = models.ForeignKey('self', **options)
                    hist_field.name = field.name
                    hist_field.attname = field.attname
                    field = hist_field
                elif is_versioned(field.related.parent_model):
                    # Make the field into a foreignkey pointed at the
                    # history model.
                    fk_history_model = field.related.parent_model.history.model
                    options = _get_fk_opts(field)

                    hist_field = models.ForeignKey(fk_history_model, **options)
                    hist_field.name = field.name
                    hist_field.attname = field.attname
                    field = hist_field

            #if isinstance(field, models.ForeignKey):
            #    # If the related model is also versioned then we will
            #    # use a custom IntegerField instead. This is to prevent
            #    # deletion of a versioned model instance from cascading
            #    # and deleting historical versions of related objects.
            #    if is_versioned(field.related.parent_model):
            #        field = VersionedForeignKey(field)
            #    else:
            #        if field.rel.related_name is not None:
            #            # custom related_name is set so we have to
            #            # rename it or we'll have a collision
            #            field.rel.related_name = "%s_hist" % field.rel.related_name

            #if isinstance(field, models.ManyToManyField):
            #    opts = _get_m2m_opts(field)
            #    field = models.ManyToManyField(opts)

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

    META_TO_SKIP = [
        'db_table', 'get_latest_by', 'managed', 'unique_together', 'ordering',
    ]
    def get_meta_options(self, model):
        """
        Returns a dictionary of fields that will be added to
        the Meta inner class of the track changes model.
        """
        meta = { 'ordering': ('-history_date',) }
        for k in ALL_META_OPTIONS:
            if k in TrackChanges.META_TO_SKIP: continue 
            meta[k] = getattr(model._meta, k)
        return meta

    def post_save(self, instance, created, **kws):
        history_type = getattr(instance, '_history_type', None)
        is_revert = history_type == TYPE_REVERTED
        if created:
            history_type = TYPE_REVERTED_ADDED if is_revert else TYPE_ADDED
        else:
            history_type = history_type or TYPE_UPDATED
        self.create_historical_record(instance, history_type)

    def pre_delete(self, instance, **kws):
        self._pk_recycle_cleanup(instance)

        #self._pre_delete_related_objects(instance)
    
    def post_delete(self, instance, **kws):
        history_type = getattr(instance, '_history_type', None)
        is_revert = history_type == TYPE_REVERTED
        history_type = TYPE_REVERTED_DELETED if is_revert else TYPE_DELETED
        if not self._is_pk_recycle_a_problem(instance):
            self.create_historical_record(instance, history_type)

        # Disconnect the related objects signals
        if hasattr(instance, '_rel_objs_methods'):
            for model, method in instance._rel_objs_methods.iteritems():
                models.signals.pre_delete.disconnect(method, model, weak=False)

    def create_historical_record(self, instance, type):
        manager = getattr(instance, self.manager_name)
        # If they set track_changes to False
        # then we don't auto-create a revision here.
        if not instance._track_changes:
            return
        attrs = {}
        for field in instance._meta.fields:
            if isinstance(field, models.fields.related.ForeignKey):
                is_fk_to_self = field.related.parent_model == instance.__class__
                if is_versioned(field.related.parent_model) or is_fk_to_self:
                    # If the FK field is versioned, set it to the most
                    # recent version of that object.

                    # The object the FK id refers to may have been
                    # deleted so we can't simply do Model.objects.get().
                    fk_hist_model = field.rel.to.history.model
                    fk_id_name = field.rel.field_name
                    fk_id_val = getattr(instance, field.attname)
                    fk_objs = fk_hist_model.objects.filter(**{fk_id_name:fk_id_val})

                    if fk_objs:
                        attrs[field.name] = fk_objs[0] # most recent version
                    else:
                        attrs[field.name] = None
                    continue
            attrs[field.attname] = getattr(instance, field.attname)
        attrs.update(self._get_save_with_attrs(instance))
        #attrs = self._get_save_with_attrs(instance)
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
        if (settings.DATABASE_ENGINE == 'sqlite3' and
            not unique_lookup_values_for(instance)):
            return True

    def _pk_recycle_cleanup(self, instance):
        """
        SQLite recycles autofield primary keys. Oops!
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
