from django import forms

from versionutils.versioning.forms import CommentMixin
from pages.models import Page
from pages.fields import PageChoiceField
from utils.static import static_url

from models import Redirect


class RedirectForm(CommentMixin, forms.ModelForm):
    destination = PageChoiceField(queryset=Page.objects.all())

    class Meta:
        model = Redirect

    class Media:
        js = (
              static_url('js/jquery/jquery-1.7.min.js'),
              static_url('js/jquery/jquery-ui-1.8.16.custom.min.js'),
        )
