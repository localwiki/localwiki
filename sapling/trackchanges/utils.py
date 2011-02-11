from collections import defaultdict
from functools import partial

from django.db import models

def is_versioned(m):
    """
    @param m: A model instance or class.
    @returns: True if the model has changes tracked.
    """
    return (getattr(m, '_history_manager_name', None) is not None)

def unique_lookup_values_for(m):
    """
    Returns a name: value dictionary of the unique fields of the
    model instance m.

    @param m: An instance of a model.
    """
    for field in m._meta.fields:
        if field.primary_key or field.auto_created: continue
        if not field.unique: continue

        return { field.name: getattr(m, field.name) }

    if m._meta.unique_together:
        unique_fields = {}
        # tuple of field names, e.g. ('email', 'cellphone')
        for k in m._meta.unique_together[0]:
            unique_fields[k] = getattr(m, k)
        return unique_fields

def _related_objs_delete_passalong(m):
    """
    For all related objects, set _track_changes and _save_with
    accordingly.

    @param m: a model instance
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
    related_versioned = [ o for o in related_objects if is_versioned(o.model) ]
    # Using related objs, build a dictionary mapping model class -> pks
    for rel_o in related_versioned:
        accessor = rel_o.get_accessor_name()
        if not hasattr(m, accessor):
            continue
        objs = getattr(m, accessor).all()
        for o in objs:
            # We use a dictionary for fast lookup in
            # _set_arguments_for
            m._rel_objs_to_catch[o.__class__][o.pk] = True

    # Construct a method that will check to see if the sender is
    # one of the related objects
    for model in m._rel_objs_to_catch:
        ids_to_catch = m._rel_objs_to_catch[model]
        _pass_on_arguments = partial(_set_arguments_for, m, model, ids_to_catch)
        models.signals.pre_delete.connect(_pass_on_arguments, sender=model, weak=False)
        # Save the method so we can disconnect it
        m._rel_objs_methods[model] = _pass_on_arguments

def save_with_arguments(m, force_insert=False, force_update=False, using=None,
                        track_changes=True, **kws):
    """
    A simple custom save() method on models with changes tracked.

    NOTE: All essential logic should go into our post/pre-delete/save
          signal handlers, NOT in this method. Custom delete()
          methods aren't called when doing bulk QuerySet.delete().
    """
    m._track_changes = track_changes
    m._save_with = kws
    return super(m.__class__, m).save(force_insert=force_insert,
                                      force_update=force_update,
                                      using=using,
    )

def delete_with_arguments(m, using=None, track_changes=True, **kws):
    """
    A simple custom delete() method on models with changes tracked.

    NOTE: Most history logic should go into our post/pre-delete/save
          signal handlers, NOT in this method. Custom delete()
          methods aren't called when doing bulk QuerySet.delete().
    """
    m._track_changes = track_changes
    m._save_with = kws

    _related_objs_delete_passalong(m)
    return super(m.__class__, m).delete(using=using)
