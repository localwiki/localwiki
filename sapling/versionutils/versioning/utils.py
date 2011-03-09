from collections import defaultdict
from functools import partial

from django.db import models
from django.conf import settings
from django.db.models.sql.constants import LOOKUP_SEP


def is_versioned(m):
    """
    Args:
        m: A model instance or model class.

    Returns:
        True if the model has changes tracked.
    """
    return (getattr(m, '_history_manager_name', None) is not None)


def is_directly_versioned(m):
    """
    Args:
        m: A Model instance or a model class.

    Returns:
        True if the model is *directly* versioned by having TrackChanges
        on its own class definition.  Generally speaking, you want to use
        is_versioned rather than this method.
    """
    if not is_versioned(m):
        return False
    is_class = isinstance(m, type)
    hist_manager = getattr(m, getattr(m, '_history_manager_name'))

    if is_class:
        return (hist_manager.model._original_model == m)
    return (hist_manager.model._original_model == m.__class__)


def is_historical_instance(m):
    """
    Is the provided instance a historical instance?
    """
    return (hasattr(m, '_original_model') and
            is_versioned(m._original_model))


def get_parent_instance(m, parent):
    """
    Attrs:
        m: Instance of child model.
        parent: Parent class.

    Returns:
        The instance of the parent associated with the child model in the
        case of concrete model inheritence.  Returns None if there's no
        parent instance associated with m.
    """
    if m.__class__ != parent and issubclass(m.__class__, parent):
        for f in m.__class__._meta.fields:
            # Concrete model inheritence.
            if getattr(f, 'rel', None) and f.rel.parent_link:
                parent_instance = getattr(m, f.related.field.name)
                return parent_instance
    return None


def unique_lookup_values_for(m):
    """
    Args:
        m: A model instance.

    Returns:
        A {name: value} dictionary of the unique fields of the
        model instance m.
    """
    for field in m._meta.fields:
        if field.primary_key or field.auto_created:
            continue
        if not field.unique:
            continue
        is_onetoone = (
            hasattr(field, 'related') and
            field.related.field.__class__ == models.OneToOneField
        )
        if is_onetoone and is_versioned(field.related.model):
            # If the OneToOneField is versioned then we return something
            # along the lines of fieldname__pk=m.pk.  We do this
            # because on historical models, foreign keys to versioned
            # models point right to their historical model form.  So we
            # normally do things like
            # p.history.filter(fk=historical_fk).  To build this unique
            # dictionary we need to use the pk of the provided
            # NON-historical object, m.

            # For OneToOneFields, attname is "b_id"
            related_pk = getattr(m, field.attname)
            k = "%s%sid" % (field.name, LOOKUP_SEP)
            v = related_pk
            return {k: v}

        return {field.name: getattr(m, field.name)}

    if m._meta.unique_together:
        unique_fields = {}
        # See note about OneToOneFields above.
        onetoone_versioned = []
        for field in m._meta.fields:
            is_onetoone = (
                hasattr(field, 'related') and
                field.related.field.__class__ == models.OneToOneField
            )
            if is_onetoone and is_versioned(field.related.model):
                onetoone_versioned.append(field.name)

        # Tuple of field names, e.g. ('email', 'cellphone')
        for k in m._meta.unique_together[0]:
            # Do fancy lookup for versioned OneToOneFields.
            if k in onetoone_versioned:
                k = "%s%sid" % (field.name, LOOKUP_SEP)
                v = getattr(m, field.name).pk
                unique_fields[k] = v
            else:
                unique_fields[k] = getattr(m, k)
        return unique_fields


def is_pk_recycle_a_problem(instance):
    if (settings.DATABASE_ENGINE == 'sqlite3' and
        not unique_lookup_values_for(instance)):
        return True



