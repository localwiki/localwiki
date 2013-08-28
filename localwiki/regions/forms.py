from django.conf import settings
from django.forms import ValidationError

from olwidget import widgets
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
            raise ValidationError("Please draw a region with the map drawing tool.")
        return data
