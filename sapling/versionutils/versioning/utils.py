from django.db import models
from django.conf import settings
from django.db.models.sql.constants import LOOKUP_SEP

import exceptions


def is_versioned(m):
    """
    Args:
        m: A model instance or model class.

    Returns:
        True if the model has changes tracked.
    """
    history_manager_name = getattr(m, '_history_manager_name', None)
    if history_manager_name is None:
        return False

    # If all we did was check for the existance of the
    # history_manager_name manager on m then we'd get tripped up in the
    # case of model inheritance. E.g. we could have model B extending
    # model A, with model A versioned -- and so A would pass along its
    # _history_manager_name attribute to B via inheritance but B isn't
    # itself versioned.
    versions = getattr(m, history_manager_name)
    model_thats_versioned = versions.model._original_model

    if isinstance(m, models.Model):
        return type(m) == model_thats_versioned
    else:
        return m == model_thats_versioned


def get_versions(m):
    """
    Args:
        m: A model instance or model class.

    Returns:
        The historical manager for m.

    Raises:
        versioning.exceptions.ModelNotVersioned exception if m is not
            versioned.
    """
    history_manager_name = getattr(m, '_history_manager_name', None)
    if history_manager_name is None:
        raise exceptions.ModelNotVersioned(
            "%s is not a versioned model" % m)
    return getattr(m, history_manager_name)


def is_directly_versioned(m):
    """
    Args:
        m: A Model instance or a model class.

    Returns:
        True if the model is registered *directly* with versioning.register.
        Generally speaking, you want to use is_versioned rather than this
        method.
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


def get_related_versioned_fields(m):
    """
    Args:
        m: A model instance or model class.

    Returns:
        A list of the fields attached to m which are versioned.
    """
    fields = []
    rel_fields = [f for f in m._meta.fields if hasattr(f, 'related')]
    for field in rel_fields:
        if is_versioned(field.related.parent_model):
            fields.append(field)
    return fields


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
        if is_onetoone and is_versioned(field.related.parent_model):
            # If the OneToOneField is versioned then we return something
            # along the lines of fieldname__pk=m.pk.  We do this
            # because on historical models, foreign keys to versioned
            # models point right to their historical model form.  So we
            # normally do things like
            # p.versions.filter(fk=historical_fk).  To build this unique
            # dictionary we need to use the pk of the provided
            # NON-historical object, m.

            # Get the unique fields of the related model.
            parent_model = field.related.parent_model
            try:
                parent_instance = getattr(m, field.name)
            except parent_model.DoesNotExist:
                # parent_instance is currently deleted.  Let's look up
                # the most recent historical version and use that to get
                # the unique fields.
                pk_name = parent_model._meta.pk.name
                hist_name = getattr(parent_model, '_history_manager_name')
                versions = getattr(parent_model, hist_name)
                parent_hist_instance = versions.filter(
                    **{pk_name: getattr(m, field.attname)})[0]
                parent_instance = parent_hist_instance.version_info._object

            parent_unique = unique_lookup_values_for(parent_instance)
            if not parent_unique:
                # E.g. {'id': 3}
                parent_pk_name = parent_instance._meta.pk.name
                parent_unique = {parent_pk_name: parent_instance.pk}

            uniques = {}
            for parent_k, parent_v in parent_unique.iteritems():
                # Create something like {'page__id': 3} or
                # {'page__slug': 'front page'}
                k = "%s%s%s" % (field.name, LOOKUP_SEP, parent_k)
                uniques[k] = parent_v
            return uniques

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
