################################################
# This is a thin wrapper over olwidget.
# We provide our own media.
################################################
from django.conf import settings

from olwidget import widgets
from utils import reverse_lazy
from utils.static_helpers import static_url

OUR_JS = [
    reverse_lazy('django.views.i18n.javascript_catalog',
                   args=['maps']),
    static_url('js/jquery/jquery-1.7.min.js'),
    static_url('olwidget/js/sapling_utils.js'),
]
OUR_CSS = {}


class MediaMixin(object):
    class Media:
        js = OUR_JS
        css = OUR_CSS


class InfoMap(MediaMixin, widgets.InfoMap):
    pass

    def __init__(self, *args, **kwargs):
        val = super(InfoMap, self).__init__(*args, **kwargs)
        # Potentially limit # of layers on InfoMaps, for now. This helps
        # with quicker load times on most pages.
        max_layers = getattr(settings, 'OLWIDGET_INFOMAP_MAX_LAYERS', 1)
        self.options['layers'] = self.options['layers'][:max_layers]
        return val

