=========
Extending
=========

Adding extra fields to historical models
----------------------------------------

You can subclass :class:`ChangesTracker` to provide extra fields on
historical record models.  Then, when doing `versioning.register`, pass
in your custom changes tracker class.  You'll want to override the
:func:`get_extra_history_fields` method in your :class:`ChangesTracker`
subclass:

    .. method:: get_extra_history_fields(model):

        Extra, non-essential fields for the historical models.

        If you subclass TrackChanges this is a good method to over-ride:
        simply add your own values to the fields for custom fields.

        NOTE: Your custom fields should start with history_ if you want them
              to be looked up via hm.version_info.fieldname

        Returns:
            A dictionary of fields that will be added to the historical
            record model.
