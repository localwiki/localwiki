from django.db import models
from django import forms

from django.forms.models import model_to_dict

from versionutils.versioning.utils import is_versioned
from versionutils.versioning import get_versions


class MergeMixin(object):
    """
    ModelForm mixin that detects editing conflicts.  For example, consider
    the following scenario:

    User A obtains a form to edit model instance M
    User B obtains a form to edit the same instance
    User B makes some changes and submits the form.  M is updated.
    User A makes some changes and submits the form.  B's changes are lost.

    MergeMixin will check to see if anyone else has edited the
    associated model since the form was loaded.  If so, a ValidationError is
    raised with the provided conflict_error.

    To perform a merge in this case, simply subclass MergeMixin and provide
    your own merge() method.

    As long as the associated model is versioned using versioning.register
    or has a DateTimeField with auto_now=True this will work automatically.
    Otherwise you'll want to subclass MergeMixin and override
    get_version_date().

    NOTE: You need to list MergeMixin before ModelForm in your
    subclasses list.  Example::

        class PageForm(MergeMixin, forms.ModelForm):
            class Meta:
                model = Page
                fields = ('content',)

    Attributes:
        conflict_error: The optional warning string to return alongside
            ValidationError on a conflict.
        merge_success_msg: The optional string to send as a message if a
            merge successfully occurs.
        version_date_field: Optional field name to use for figuring out
            the version date.  We infer this automatically if the associated
            model is versioned using versioning.register or has an
            auto_now=True DateTimeField.  You probably want to override
            get_version_date() instead of using this attribute.
    """
    version_date = forms.CharField(widget=forms.HiddenInput(), required=False)
    conflict_error = ('Warning: someone else made changes before you.  '
        'Please review the changes and save again.')
    merge_success_msg = ('Someone else made changes before you but your '
        'changes were successfully merged.')

    def __init__(self, *args, **kwargs):
        base_init = super(MergeMixin, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.initial['version_date'] = str(self.get_version_date(instance))
        # Due to mixin behavior we need to set this here, too.
        self.fields['version_date'] = self.version_date

        self.performed_merge = False
        return base_init

    def get_version_date(self, instance):
        """
        Gets the datetime the instance was last modified.  This default
        implementation either uses the field specified by version_date_field
        or grabs a DateTimeField with auto_now=True.

        Override this method to customize how you want to determine the
        version date.
        """
        if hasattr(self, 'version_date_field'):
            return getattr(instance, self.version_date_field)

        # if using versioning, return most recent version date
        if is_versioned(instance):
            try:
                return get_versions(instance).most_recent().version_info.date
            except:
                return ''

        # no version_date_field specified, let's try to guess it
        date_fields = [field for field in instance._meta.fields
                        if isinstance(field, models.DateTimeField) and
                           field.auto_now]
        if date_fields:
            return getattr(instance, date_fields[0].name) or ''

        raise ValueError('MergeMixin cannot find a version_date_field')

    def merge(self, yours, theirs, ancestor):
        """
        Merges the different versions of the object's fields in case of a
        conflict.  Override this to provide the actual merging.

        Just like clean(), this should return a dictionary of cleaned fields
        that should be used.

        Suggested use: override and try to merge the fields.  If the merge
        does not have any conflicts, return a dictionary of the merged fields.
        Otherwise, raise a helpful ValidationError, optionally setting
        self.data to something useful, such as the merged fields with
        conflicts, for the user to resolve.

        Attrs:
            yours: A dictionary of the current form's cleaned fields.
            theirs: A dictionary of the initial data from the instance.
            ancestor: A dictionary of the historic ancestor's data, if
                available, or None

        Returns:
            A dictionary of cleaned and merged fields, similar to clean().
        """
        raise forms.ValidationError(self.conflict_error)

    def clean(self):
        """
        Detects when the instance is newer than the one used to generate the
        form.  Calls merge() when there is a version conflict, and if there is
        still an error, updates the version date in the form to give the user
        a chance to save anyway.

        Returns
            cleaned_data.

        Raises:
            ValidationError: When there's a conflict when calling merge().
        """
        self.cleaned_data = super(self.__class__.__base__, self).clean()

        current_version_date = str(self.get_version_date(self.instance))
        form_version_date = self.data['version_date']
        if current_version_date != form_version_date:
            ancestor = None
            if is_versioned(self.instance) and form_version_date:
                ancestor_model = get_versions(self.instance).as_of(
                    form_version_date)
                ancestor = model_to_dict(ancestor_model)
            try:
                self.cleaned_data = self.merge(self.cleaned_data, self.initial,
                                               ancestor)
            except forms.ValidationError as e:
                self.data = self.data.copy()
                self.data['version_date'] = current_version_date
                raise e
            else:
                # Note that we performed a merge, for use elsewhere.
                self.performed_merge = True
        return self.cleaned_data
