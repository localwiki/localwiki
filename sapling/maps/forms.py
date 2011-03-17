from django import forms

from olwidget.forms import MapModelForm

from models import MapData


class MapForm(MapModelForm):  # MergeModelForm):
    class Meta:
        model = MapData
        exclude = ('page',)
