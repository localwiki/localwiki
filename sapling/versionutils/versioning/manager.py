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
        # Get the variable names of related, versioned objects.
        rels = self.model._original_model._meta.get_all_related_objects()
        versioned_vars = [o.var_name for o in rels if is_versioned(o.model)]

        # Get the lookup names of versioned parent models.
        parents = self.model._original_model._meta.parents
        versioned_parents = []
        for k, v in parents.iteritems():
            if is_versioned(k):
                versioned_parents.append(v.name)

        # Iterate through the provided keywords, replacing certain
        # attributes with ones that correspond to historical models.
        kws_new = {}
        for k, v in kws.iteritems():
            k_new = k
            parts = k.split(models.sql.constants.LOOKUP_SEP)
            # Replace all instances of version_info__whatever with
            # history_whatever.
            if len(parts) > 1 and parts[0] == 'version_info':
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
            # Replace all instances of parent_ptr__whatever
            # with parent_hist_ptr__whatever if parent's versioned.
            if parts[0] in versioned_parents:
                rest = models.sql.constants.LOOKUP_SEP.join(parts[2:])
                if rest:
                    rest = "%s%s" % (models.sql.constants.LOOKUP_SEP, rest)
                # -4 will remove '_ptr' from the original string.
                k_new = '%s_hist_ptr%s' % (parts[0][:-4], rest)

            kws_new[k_new] = v

        return super(HistoricalMetaInfoQuerySet, self).filter(*args, **kws_new)


class HistoryManager(models.Manager):
    def __init__(self, model, instance=None):
        super(HistoryManager, self).__init__()
        self.model = model
        self.instance = instance

        parent_instance = get_parent_instance(
            self.instance, model._original_model)
        if parent_instance:
            # Having a parent instance means we are doing concrete model
            # inheritence.  In this case, we want to return a QuerySet
            # associated with the parent historical instance.  If the
            # child is also versioned then the child will attach its own
            # HistoryManager instance which will over-ride this.
            self.instance = parent_instance

    def create(self, **kwargs):
        return QuerySet(self.model, using=self._db).create(**kwargs)

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
                pk_name = self.instance._meta.pk.name
                # Having a related object for a pk implies that this is
                # a concretely subclassed object.  We need to use an
                # integer lookup in this case.
                if getattr(self.instance._meta.pk, 'rel', None):
                    # We normally use the history_id to do the lookup,
                    # but if the parent model is versioned then the pk
                    # on the child (historical) model will be a parent
                    # pointer, so we want this lookup be of the form
                    # parentmodel_hist_ptr__id rather than
                    # parentmodel_ptr__id.
                    original_base = getattr(self.model.__base__,
                                            '_original_model', None)
                    if original_base and is_versioned(original_base):
                        pk_name = "%s%sid" % (
                            # Use historical model's pk name of the form
                            # parentmodel_hist_ptr.
                            self.model._meta.pk.name,
                            models.sql.constants.LOOKUP_SEP)

                filter = {pk_name: self.instance.pk}
            else:
                raise self.NoUniqueValuesError(
                    "Wasn't passed an active (existing) instance and model "
                    "has no unique fields or no unique_together defined!"
                )

        return HistoricalMetaInfoQuerySet(model=self.model).filter(**filter)

    def most_recent(self):
        """
        Returns:
            The most recent historical record instance.

        Raises:
            DoesNotExist: Instance has no historical record.
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
        Args:
            date: A datetime object.  The datetime doesn't have to be
                exact.  We will return the historical instance that's
                most recent, moving backward in time.
            version: An integer version number.

        Returns:
            A historical record instance that represents the object as
            it was at the date or version number provided.

        Raises:
            DoesNotExist: Instance hasn't been created yet.
        """
        try:
            if version and version > 0:
                v = self.all().order_by('history_date')[version - 1]
            elif date:
                v = self.filter(history_date__lte=date)[0]
        except IndexError:
            raise self.instance.DoesNotExist("%s hasn't been created yet." %
                    self.instance._meta.object_name)

        return v

    class NoUniqueValuesError(Exception):
        pass
