from django import forms


class CommentMixin(object):
    """
    ModelForm mixin that adds a comment field to the form.  When the
    ModelForm is saved the comment is set on the historical instance.

    NOTE: You need to list CommentMixin before ModelForm in your
    subclasses list.  Example::

        class PageForm(CommentMixin, forms.ModelForm):
            class Meta:
                model = Page
                fields = ('content',)
    """
    comment = forms.CharField(max_length=150, required=False)

    def __init__(self, *args, **kwargs):
        base_init = super(CommentMixin, self).__init__(*args, **kwargs)
        # Due to mixin behavior we need to set this here, too.
        self.fields['comment'] = self.comment
        return base_init

    def save(self, commit=True):
        # It would be ideal if the ModelForm save method took keyword
        # arguments and passed them along.
        save_with = getattr(self.instance, '_save_with', {})
        comment = self.cleaned_data.get('comment')
        if comment:
            save_with['comment'] = comment
        self.instance._save_with = save_with
        return super(CommentMixin, self).save(commit=commit)


class DeleteForm(forms.Form):
    """
    The default form displayed when using versioning.views.DeleteView.

    Contains a single comment field.
    """
    comment = forms.CharField(max_length=150, required=False,
        label="Reason for deletion")


class RevertForm(forms.Form):
    """
    The default form displayed when using versioning.views.RevertView.

    Contains a single comment field.
    """
    comment = forms.CharField(max_length=150, required=False,
        label="Reason for revert")
