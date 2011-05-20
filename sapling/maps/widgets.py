################################################
# This is a thin wrapper over olwidget.
# We provide our own media.
################################################

from django.conf import settings
from django import forms

from olwidget import widgets

OUR_JS = [
    '%solwidget/js/sapling_utils.js' % settings.STATIC_URL,
    '%sjs/jquery/jquery-1.5.min.js' % settings.STATIC_URL,
]
OUR_CSS = {}


class MediaMixin(object):
    class Media:
        js = OUR_JS
        css = OUR_CSS


class InfoMap(MediaMixin, widgets.InfoMap):
    pass
