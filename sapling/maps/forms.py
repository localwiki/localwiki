from django.conf import settings

from olwidget.forms import MapModelForm

from models import MapData

OLWIDGET_OPTIONS = None
if hasattr(settings, 'OLWIDGET_DEFAULT_OPTIONS'):
    OLWIDGET_OPTIONS = settings.OLWIDGET_DEFAULT_OPTIONS


class MapForm(MapModelForm):  # MergeModelForm):
    class Meta:
        model = MapData
        exclude = ('page',)
        options = OLWIDGET_OPTIONS
