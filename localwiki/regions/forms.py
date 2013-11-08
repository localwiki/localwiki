from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy

from olwidget.widgets import EditableMap
from olwidget.forms import MapModelForm

from localwiki.utils import reverse_lazy
from localwiki.utils.static_helpers import static_url

from models import Region


OUR_JS = [
    reverse_lazy('django.views.i18n.javascript_catalog',
                   args=['maps']),
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
    class Meta:
        model = Region

    def clean_geom(self):
        data = self.cleaned_data['geom']
        if not data or not data[0]:
            raise forms.ValidationError("Please draw a region with the map drawing tool.")
        return data


class RegionSettingsForm(MediaMixin, forms.Form):
    full_name = forms.CharField(max_length=255,
        help_text=ugettext_lazy("The full name of this region, e.g. 'San Francisco'"))
    geom = forms.CharField(widget=EditableMap({'geometry': 'polygon'}))


#class RegionAdminsForm(MediaMixin, forms.Form):
#    full_name = forms.CharField(max_length=255,
#        help_text=ugettext_lazy("The full name of this region, e.g. 'San Francisco'"))
#    geom = forms.CharField(widget=EditableMap({'geometry': 'polygon'}))
