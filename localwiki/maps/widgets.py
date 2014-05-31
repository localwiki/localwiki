################################################
# This is a thin wrapper over olwidget.
# We provide our own media.
################################################
from copy import copy

from django.conf import settings

from olwidget import widgets
from utils import reverse_lazy
from utils.static_helpers import static_url

OUR_JS = [
    static_url('olwidget/js/sapling_utils.js'),
]
OUR_CSS = {}


class MediaMixin(object):
    class Media:
        js = OUR_JS
        css = OUR_CSS


class InfoMap(MediaMixin, widgets.InfoMap):
    def __init__(self, *args, **kwargs):
        val = super(InfoMap, self).__init__(*args, **kwargs)
        # Potentially limit # of layers on InfoMaps, for now. This helps
        # with quicker load times on most pages.
        max_layers = getattr(settings, 'OLWIDGET_INFOMAP_MAX_LAYERS', 1)
        controls = self.options.get('map_options', {}).get('controls', [])
        # TODO: This is an ugly hack caused by the fact we hard-coded map
        # controls into localsettings.py, making this sort of thing difficult
        # to change without a hack like this.  Break out map controls, etc
        # to some other place later.
        if 'PanZoomBar' in controls:
            controls.remove('PanZoomBar')
            controls.append('PanZoom')
        self.options['layers'] = self.options['layers'][:max_layers]
        return val


def map_options_for_region(region):
    region_center = region.regionsettings.region_center
    if not region_center:
        return {}
    opts = {
        'default_lon': region_center.x,
        'default_lat': region_center.y,
        'default_zoom': region.regionsettings.region_zoom_level,
    }
    layers = copy(getattr(settings, 'OLWIDGET_DEFAULT_OPTIONS')['layers'])
    opts['layers'] = layers
    return opts
