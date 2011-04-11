=========
Extending
=========

Adding extra fields to historical models
----------------------------------------

You can subclass :class:`TrackChanges` to provide extra fields on
historical record models.  Simply override the
:func:`get_extra_history_fields` method:

    .. method:: get_extra_history_fields(model):

        Extra, non-essential fields for the historical models.

        If you subclass TrackChanges this is a good method to over-ride:
        simply add your own values to the fields for custom fields.

        NOTE: Your custom fields should start with history_ if you want them
              to be looked up via hm.history_info.fieldname

        Returns:
            A dictionary of fields that will be added to the historical
            record model.
