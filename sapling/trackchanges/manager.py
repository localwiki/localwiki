from django.db import models
from django.db.models.query import QuerySet

from utils import *
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

class HistoricalMetaInfoQuerySet(QuerySet):
    """
    Simple QuerySet to make filtering intuitive.
    """
    def filter(self, *args, **kws):
        """
        Replace all instances of history_info__whatever with
        history_whatever.
        """
        kws_new = {}
        for k,v in kws.iteritems():
            k_new = k
            parts = k.split(models.sql.constants.LOOKUP_SEP)
            if len(parts) > 1 and parts[0] == 'history_info':
                rest = models.sql.constants.LOOKUP_SEP.join(parts[2:])
                if rest:
                    rest = "%s%s" % (models.sql.constants.LOOKUP_SEP, rest)
                k_new = 'history_%s%s' % (parts[1], rest)

            kws_new[k_new] = v

        return super(HistoricalMetaInfoQuerySet, self).filter(*args, **kws_new)

class HistoryManager(models.Manager):
    def __init__(self, model, instance=None):
        super(HistoryManager, self).__init__()
        self.model = model
        self.instance = instance
        # setting this to false turns off
        # auto-generation of revisions in the history
        # table on save.
        self.track_changes = True

    def get_query_set(self):
        if self.instance is None:
            return HistoricalMetaInfoQuerySet(model=self.model)
        
        # Note: We can't use Django 1.2's natural_key() method here because
        # it doesn't necessarily return model attributes - it can literally
        # return anything as long as that anything can be used by
        # get_by_natural_key() to do a lookup. For instance, natural_key()
        # could return values that are used by get_by_natural_key() to look
        # up an object's pk in an external database.
        unique_fields = unique_fields_of(self.instance)
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

        return HistoricalMetaInfoQuerySet(model=self.model).filter(**filter)

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

    class NoUniqueValuesError(Exception):
        pass
