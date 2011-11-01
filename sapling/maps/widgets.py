################################################
# This is a thin wrapper over olwidget.
# We provide our own media.
################################################
from urlparse import urljoin

from django.conf import settings

from olwidget import widgets
from utils.static import static_url

OUR_JS = [
    static_url('js/jquery/jquery-1.6.4.min.js'),
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
        # Just display one layer for InfoMaps, for now.
        if len(self.options['layers']) > 1:
            self.options['layers'] = self.options['layers'][:1]
        return val

