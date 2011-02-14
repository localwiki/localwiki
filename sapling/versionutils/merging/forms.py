from django.db import models
from django import forms

class MergeModelForm(forms.ModelForm):
    """
    ModelForm subclass that detects editing conflicts.  For example, consider the following scenario:
    
    User A obtains a form to edit model instance M
    User B obtains a form to edit the same instance
    User B makes some changes and submits the form.  M is updated.
    User A makes some changes and submits the form.  B's changes are lost.
    
    To avoid this, MergeModelForm adds a version_date parameter to the form and checks that it's still current
    when the form is submitted.  If not, a helpful message is displayed, and the user is allowed to try again.
    As long as the model has a DateTimeField with auto_now=True, version_date will be guessed automatically.
    To customize how the version_date is determined, set self.verson_date_field to the name of the field to use
    or override get_version_date().
    """
    version_date = forms.CharField(widget=forms.HiddenInput(), required=False)
    conflict_warning = 'Warning: someone else made changes before you.  Please review the changes and save again.'
    
    def __init__(self, *args, **kwargs):
        super(MergeModelForm, self).__init__(*args, **kwargs)
        
        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.initial['version_date'] = str(self.get_version_date(instance))
    
    def get_version_date(self, instance):
        """
        Gets the datetime the instance was last modified.  This default implementation either uses the field
        specified by version_date_field or grabs a DateTimeField with auto_now=True.
        Override this method to customize how you want to determine the version date.
        """
        if hasattr(self, 'version_date_field'):
            return getattr(instance, self.version_date_field)
        
        # no version_date_field specified, let's try to guess it
        # TODO: support for track_changes.
        date_fields = [field for field in instance._meta.fields if isinstance(field, models.DateTimeField) and field.auto_now]
        if date_fields:
            return getattr(instance, date_fields[0].name) or ''
        
        raise ValueError('MergeModelForm does not have a version_date_field')
    
    def merge(self, yours, theirs, ancestor):
        """
        Merges the different versions of the object's fields in case of a conflict.
        Override this to provide the actual merging.  Just like clean(), this should return a dictionary
        of cleaned fields that should be used.
        Suggested use: override and try to merge the fields.  If the merge does not have any conflicts, return
        a dictionary of the merged fields.  Otherwise, raise a helpful ValidationError, optionally setting
        self.data to something useful, such as the merged fields with conflicts, for the user to resolve.
        
        @param yours: a dictionary of the current form's cleaned fields
        @param theirs: a dictionary of the initial data from the instance
        @param ancestor: a dictionary of the historic ancestor's data, if available, or None
        @return: a dictionary of cleaned and merged fields, similar to clean()
        """
        raise forms.ValidationError(self.conflict_warning)
            
    
    def clean(self):
        """
        Detects when the instance is newer than the one used to generate the form.
        Calls merge() when there is a version conflict, and if there is still an error, updates
        the version date in the form to give the user a chance to save anyway.
        """
        current_version_date = str(self.get_version_date(self.instance))
        if current_version_date != self.data['version_date']:
            try:
                self.cleaned_data = self.merge(self.cleaned_data, self.initial, None)
            except forms.ValidationError as e:
                self.data = self.data.copy()
                self.data['version_date'] = current_version_date
                raise e
        return self.cleaned_data
