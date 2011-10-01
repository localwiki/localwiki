from django import forms

from versionutils.versioning.forms import CommentMixin
from pages.models import Page
from pages.fields import PageChoiceField

from models import Redirect


class RedirectForm(CommentMixin, forms.ModelForm):
    destination = PageChoiceField(queryset=Page.objects.all())

    class Meta:
        model = Redirect
