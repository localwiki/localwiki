from django.db import models

from decorators import *

class HistoryDescriptor(object):
    def __init__(self, model):
        self.model = model

    def __get__(self, instance, owner):
        if instance is None:
            if not hasattr(self, '_history_manager_global'):
                self._history_manager_global = HistoryManager(self.model)
            return self._history_manager_global
        if not hasattr(instance, '_history_manager'):
            instance._history_manager = HistoryManager(self.model, instance)
        return instance._history_manager

class HistoryManager(models.Manager):
    def __init__(self, model, instance=None):
        super(HistoryManager, self).__init__()
        self.model = model
        self.instance = instance
        self._save_with = {}
        # setting this to false turns off
        # auto-generation of revisions in the history
        # table on save.
        self.track_changes = True

    def get_query_set(self):
        if self.instance is None:
            return super(HistoryManager, self).get_query_set()
        
        # Note: We can't use Django 1.2's natural_key() method here because
        # it doesn't necessarily return model attributes - it can literally
        # return anything as long as that anything can be used by
        # get_by_natural_key() to do a lookup. For instance, natural_key()
        # could return values that are used by get_by_natural_key() to look
        # up an object's pk in an external database.
        unique_fields = self._instance_unique_fields()
        filter = unique_fields
        # We look up based on unique fields whenever possible
        # and, as a fallback, use the primary key. This is because we'd like
        # to allow creation -> deletion -> re-creation (w/ uniques the same)
        # to pull up the right history, even if the autofield primary key
        # has changed underneath.
        if not unique_fields:
            if self.instance.pk:
                filter = {self.instance._meta.pk.name: self.instance.pk}
            else:
                raise self.NoUniqueValuesError(
                    "Wasn't passed an active (existing) instance and model "
                    "has no unique fields or no unique_together defined!"
                )

        return super(HistoryManager, self).get_query_set().filter(**filter)

    @require_instance
    def most_recent(self):
        """
        Returns the most recent copy of the history.
        """
        try:
            v = self.all()[0]
            return v
        except IndexError:
            raise self.instance.DoesNotExist("%s has no historical record." %
                                             self.instance._meta.object_name)

    @require_instance
    def as_of(self, date=None, version=None):
        """
        Returns the object as it was at the date or version number provided.

        @param date: datetime object.
        @param version: integer (version number)
        """
        try:
            if version and version > 0:
                v = self.all().order_by('history_date')[version-1]
            elif date:
                v = self.filter(history_date__lte=date)[0]
        except IndexError:
            raise self.instance.DoesNotExist("%s hasn't been created yet." %
                    self.instance._meta.object_name)
        
        return v

    def revert_to(self, delete_newer_versions=False):
        """
        This must be used on a *historical instance* - e.g. something you get
        using history.get(..) rather than an instance of the model.

        Reverts to this version of the model.

        @param delete_newer_versions: if True, delete all versions in the
               history newer than this version.
        """
        if not self.instance and not hasattr(self.instance, 'history_meta'):
            raise TypeError("revert_to() must be called via a history object. "
                            "You can get a history object by doing something "
                            "like m.history.get(...)"
            )
        # the model instance
        m = self.instance.history_meta.object
        if delete_newer_versions:
            newer = m.history.filter(date__gt=self.instance.history_meta.date)
            for v in newer:
                v.delete()
        m.save()

    def save_with(self, **kws):
        """
        Records the provided values in the historical record.

        E.g. o.history.save_with(comment="Fixing this!") will set the comment
             attribute of the historical object, if it exists.

        Call this before calling save() on your object.
        """
        # prefix all keys with 'history_' to save them into the history
        # model correctly.
        for k, v in kws.iteritems():
            self._save_with['history_%s' % k] = v

    def _instance_unique_fields(self):
        """
        Returns a name: value dictionary of the unique fields of the instance
        object.
        """
        for field in self.instance._meta.fields:
            if field.primary_key or field.auto_created: continue
            if not field.unique: continue

            # related objects have attname set to something_id for some reason
            if hasattr(field, 'related'):
                return { field.name: getattr(self.instance, field.name) }
            return { field.attname: getattr(self.instance, field.attname) }

        if self.instance._meta.unique_together:
            unique_fields = {}
            # tuple of field names, e.g. ('email', 'cellphone')
            for k in self.instance._meta.unique_together[0]:
                unique_fields[k] = getattr(self.instance, k)
            return unique_fields

    class NoUniqueValuesError(Exception):
        pass
