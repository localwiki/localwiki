from functools import partial

from django.db import models
from django.utils.functional import SimpleLazyObject

class VersionedForeignKey(models.IntegerField):
    """
    A wrapper around IntegerField used for foreign keys that are
    versioned. We need to do this to avoid deleting a versioned
    model instance during a cascade delete.
    """
    def __init__(self, fk_field, *args, **kwargs):
        super(VersionedForeignKey, self).__init__(*args, **kwargs)
        self._attribute_name = fk_field.name
        self.name = "%s_id" % fk_field.name
        self.db_index = True
        self.null = fk_field.null
        self._fk_class = fk_field.related.parent_model

    def lookup_proper_version(self, m_hist):
        """
        Returns the object pointed to by the foreign key that
        corresponds to the moment in time associated with m_hist.

        @param m_hist: A historical model instance.
        """
        def _lookup(m_hist, fk_class):
            pk = getattr(m_hist, self.name)
            as_of = m_hist.history_info.date
            return fk_class.history.filter(id=pk, history_date__lte=as_of)[0]

        do_lookup = partial(_lookup, m_hist, self._fk_class)
        return SimpleLazyObject(do_lookup)
