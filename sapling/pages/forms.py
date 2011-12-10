import mimetypes

from django import forms

from versionutils.merging.forms import MergeMixin
from versionutils.versioning.forms import CommentMixin
from pages.models import Page, PageFile, slugify
from pages.widgets import WikiEditor
from versionutils.diff.daisydiff.daisydiff import daisydiff_merge


class PageForm(MergeMixin, CommentMixin, forms.ModelForm):
    conflict_error = (
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
            raise forms.ValidationError(self.conflict_error)
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


class PageFileForm(CommentMixin, forms.ModelForm):

    def clean(self):
        self.cleaned_data = super(PageFileForm, self).clean()
        if self.instance.name:
            filename = self.cleaned_data['file'].name
            (mime_type, enc) = mimetypes.guess_type(filename)
            if mime_type != self.instance.mime_type:
                raise forms.ValidationError(
                    'The new file should be of the same type')
        return self.cleaned_data

    class Meta:
        model = PageFile
        fields = ('file',)
