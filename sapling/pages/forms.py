from django import forms
from django.template.defaultfilters import slugify

from versionutils.merging.forms import MergeMixin
from versionutils.versioning.forms import CommentMixin
from pages.models import Page
from pages.widgets import WikiEditor
from versionutils.diff.daisydiff.daisydiff import daisydiff_merge


class PageForm(MergeMixin, CommentMixin, forms.ModelForm):
    conflict_warning = (
        "Warning: someone else saved this page before you.  "
        "Please resolve edit conflicts and save again."
    )

    class Meta:
        model = Page
        fields = ('content',)
        widgets = {'content': WikiEditor()}

    def merge(self, yours, theirs, ancestor):
        # ancestor may be None
        ancestor_content = ''
        if ancestor:
            ancestor_content = ancestor['content']
        (merged_content, conflict) = daisydiff_merge(
            yours['content'], theirs['content'], ancestor_content
        )
        if conflict:
            self.data = self.data.copy()
            self.data['content'] = merged_content
            raise forms.ValidationError(self.conflict_warning)
        else:
            yours['content'] = merged_content
        return yours

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            page = Page.objects.get(slug__exact=slugify(name))
            if self.instance != page:
                raise forms.ValidationError(
                    'A page with this name already exists'
                )
        except Page.DoesNotExist:
            pass
        return name


class PageDeleteForm(forms.Form):
    comment = forms.CharField(max_length=150, required=False,
                              label="Reason for deletion")
