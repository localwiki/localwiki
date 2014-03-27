from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from olwidget.widgets import EditableMap
from olwidget.forms import MapModelForm

from localwiki.utils import reverse_lazy
from localwiki.utils.static_helpers import static_url

from models import Region, RegionSettings, BannedFromRegion, LANGUAGES


OUR_JS = [
    static_url('olwidget/js/sapling_utils.js'),
]
OUR_CSS = {}


class MediaMixin(object):
    class Media:
        js = OUR_JS
        css = OUR_CSS

################################################
# This is a thin wrapper over olwidget.
# We provide our own media.
################################################

class RegionForm(MediaMixin, MapModelForm):
    default_language = forms.ChoiceField(label=ugettext_lazy("Default language"),
        choices=LANGUAGES, required=False,
        help_text=ugettext_lazy("The language for the region"))

    class Meta:
        model = Region
        exclude = ('is_active',)

    def clean_geom(self):
        data = self.cleaned_data['geom']
        if not data or not data[0]:
            raise forms.ValidationError("Please draw a region with the map drawing tool.")
        return data


class RegionSettingsForm(MediaMixin, forms.Form):
    full_name = forms.CharField(label=ugettext_lazy("Full name"), max_length=255,
        help_text=ugettext_lazy("The full name of this region, e.g. 'San Francisco'"))
    geom = forms.CharField(widget=EditableMap({'geometry': 'polygon'}))
    default_language = forms.ChoiceField(label=ugettext_lazy("Default language"),
        choices=LANGUAGES, required=False)


class AdminSetForm(forms.ModelForm):
    model = RegionSettings
    fields = ('admins',)

    def __init__(self, *args, **kwargs):
        region = kwargs.pop('region', None)
        self.this_user = kwargs.pop('this_user', None)
        super(AdminSetForm, self).__init__(*args, **kwargs)

        from fields import UserSetField
        self.fields['admins'] = UserSetField(region=region, required=False)

    def clean_admins(self):
        admins = self.cleaned_data['admins']
        if not self.this_user in admins:
            raise forms.ValidationError(_('You cannot delete yourself as an admin'))
        return admins


class BannedSetForm(forms.ModelForm):
    model = BannedFromRegion
    fields = ('users',)

    def __init__(self, *args, **kwargs):
        region = kwargs.pop('region', None)
        self.this_user = kwargs.pop('this_user', None)
        super(BannedSetForm, self).__init__(*args, **kwargs)

        from fields import UserSetField
        self.fields['users'] = UserSetField(region=region, required=False)
