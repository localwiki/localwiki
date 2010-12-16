def is_versioned(m):
    """
    @param m: A model instance or class.
    @returns: True if the model has changes tracked.
    """
    return (getattr(m, '_history_manager_name') is not None)

def unique_fields_of(m):
    """
    Returns a name: value dictionary of the unique fields of the
    model instance m.

    @param m: An instance of a model.
    """
    for field in m._meta.fields:
        if field.primary_key or field.auto_created: continue
        if not field.unique: continue

        # related objects have attname set to something_id for some reason
        if hasattr(field, 'related'):
            return { field.name: getattr(m, field.name) }
        return { field.attname: getattr(m, field.attname) }

    if m._meta.unique_together:
        unique_fields = {}
        # tuple of field names, e.g. ('email', 'cellphone')
        for k in m._meta.unique_together[0]:
            unique_fields[k] = getattr(m, k)
        return unique_fields

def save_with_arguments(m, force_insert=False, force_update=False, using=None,
                        track_changes=True, **kws):
    m._track_changes = track_changes
    m._save_with = kws
    return super(m.__class__, m).save(force_insert=force_insert,
                                      force_update=force_update,
                                      using=using,
    )

def delete_with_arguments(m, using=None, track_changes=True, **kws):
    print "DELETE_WITH_ARGUMENTS IS BEING CALLED"
    print "!!!\nSETTING TRACK CHANGES TO", track_changes, "ON m", m, "\n!!!!!!!!"
    m._track_changes = track_changes
    print "DELETE_WITH_ARGUMENTS", id(m)
    m._save_with = kws
    return super(m.__class__, m).delete(using=using)
