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
        rels = self.model._original_model._meta.get_all_related_objects()
        versioned_vars = [ o.var_name for o in rels if is_versioned(o.model) ]
        kws_new = {}
        for k,v in kws.iteritems():
            k_new = k
            parts = k.split(models.sql.constants.LOOKUP_SEP)
            # Replace all instances of history_info__whatever with
            # history_whatever.
            if len(parts) > 1 and parts[0] == 'history_info':
                rest = models.sql.constants.LOOKUP_SEP.join(parts[2:])
                if rest:
                    rest = "%s%s" % (models.sql.constants.LOOKUP_SEP, rest)
                k_new = 'history_%s%s' % (parts[1], rest)
            # Replace all instances of fk__whatever with
            # fk_hist__whatever if fk is a versioned model.
            if parts[0] in versioned_vars:
                rest = models.sql.constants.LOOKUP_SEP.join(parts[2:])
                if rest:
                    rest = "%s%s" % (models.sql.constants.LOOKUP_SEP, rest)
                k_new = '%s_hist%s' % (parts[0], rest)

            kws_new[k_new] = v

        return super(HistoricalMetaInfoQuerySet, self).filter(*args, **kws_new)

class HistoryManager(models.Manager):
    def __init__(self, model, instance=None):
        super(HistoryManager, self).__init__()
        self.model = model
        self.instance = instance

    def get_query_set(self):
        if self.instance is None:
            return HistoricalMetaInfoQuerySet(model=self.model)
        
        # TODO: Explore using natural_key() here if it exists on the
        # model. One idea: SHA-1 an escaped, string form of the
        # natural_key() and store it as an indexed field in the
        # historical model. This may make migrations more difficult, so
        # we need to think this over. It may not be worth it, as telling
        # people to use unique / unique_together on their models is
        # reasonable and a good practice anyway.

        unique_fields = unique_lookup_values_for(self.instance)
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

        @param date: datetime object.  The datetime doesn't have to be exact.
                     We will return the historical instance that's most recent,
                     moving backward in time.
        @param version: integer (version number).
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
