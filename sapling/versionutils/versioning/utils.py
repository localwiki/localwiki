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


def is_historical_instance(m):
    """
    Is the provided instance a historical instance?
    """
    return (hasattr(m, '_original_model') and
            is_versioned(m._original_model))


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


def _related_objs_delete_passalong(m):
    """
    For all related objects, set _track_changes and _save_with
    accordingly.

    Args:
        m: A model instance.
    """
    # We use signals here.  One alternative would be to do the
    # cascade ourselves, but we can't be sure of casade behavior.
    def _set_arguments_for(child_m, model, ids_to_catch, instance, **kws):
        if instance.pk in ids_to_catch:
            instance._track_changes = child_m._track_changes
            instance._save_with = child_m._save_with

    m._rel_objs_to_catch = defaultdict(dict)
    m._rel_objs_methods = {}
    # Get the related objects.
    related_objects = m._meta.get_all_related_objects()
    related_versioned = [o for o in related_objects if is_versioned(o.model)]
    # Using related objs, build a dictionary mapping model class -> pks
    for rel_o in related_versioned:
        accessor = rel_o.get_accessor_name()
        if not hasattr(m, accessor):
            continue
        # OneToOneField means a single object.
        if rel_o.field.related.field.__class__ == models.OneToOneField:
            objs = [getattr(m, accessor)]
        else:
            objs = getattr(m, accessor).all()
        for o in objs:
            # We use a dictionary for fast lookup in
            # _set_arguments_for
            m._rel_objs_to_catch[o.__class__][o.pk] = True

    # Construct a method that will check to see if the sender is
    # one of the related objects
    for model in m._rel_objs_to_catch:
        ids_to_catch = m._rel_objs_to_catch[model]
        _pass_on_arguments = partial(_set_arguments_for, m, model,
            ids_to_catch)
        models.signals.pre_delete.connect(_pass_on_arguments, sender=model,
            weak=False)
        # Save the method so we can disconnect it
        m._rel_objs_methods[model] = _pass_on_arguments


def save_func(model_save):
    def save(m, *args, **kws):
        return save_with_arguments(model_save, m, *args, **kws)
    return save


def save_with_arguments(model_save, m, force_insert=False, force_update=False,
                        using=None, track_changes=True, **kws):
    """
    A simple custom save() method on models with changes tracked.

    NOTE: All essential logic should go into our post/pre-delete/save
          signal handlers, NOT in this method. Custom delete()
          methods aren't called when doing bulk QuerySet.delete().
    """
    m._track_changes = track_changes
    m._save_with = kws

    return model_save(m, force_insert=force_insert,
                                      force_update=force_update,
                                      using=using,
    )


def delete_func(model_delete):
    def delete(*args, **kws):
        return delete_with_arguments(model_delete, *args, **kws)
    return delete


def delete_with_arguments(model_delete, m, using=None,
                          track_changes=True, **kws):
    """
    A simple custom delete() method on models with changes tracked.

    NOTE: Most history logic should go into our post/pre-delete/save
          signal handlers, NOT in this method. Custom delete()
          methods aren't called when doing bulk QuerySet.delete().
    """
    m._track_changes = track_changes
    m._save_with = kws

    if is_pk_recycle_a_problem(m):
        m._track_changes = False

    _related_objs_delete_passalong(m)
    return model_delete(m, using=using)
