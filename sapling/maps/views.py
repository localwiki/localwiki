from django.views.generic import DetailView, UpdateView
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.conf import settings

from olwidget.widgets import InfoMap

from versionutils import diff
from utils.views import Custom404Mixin, CreateObjectMixin
from utils.views import DeleteView, RevertView, HistoryView
from pages.models import Page
from pages.models import slugify

from models import MapData
from forms import MapForm

OLWIDGET_OPTIONS = None
if hasattr(settings, 'OLWIDGET_DEFAULT_OPTIONS'):
    OLWIDGET_OPTIONS = settings.OLWIDGET_DEFAULT_OPTIONS


class MapDetailView(Custom404Mixin, DetailView):
    model = MapData

    def handler404(self, request, *args, **kwargs):
        page_slug = kwargs.get('slug')
        page = Page.objects.get(slug=slugify(page_slug))
        return HttpResponseNotFound(
            direct_to_template(request, 'maps/mapdata_new.html',
                               {'page': page})
        )

    def get_object(self):
        page_slug = self.kwargs.get('slug')
        page = Page.objects.get(slug=slugify(page_slug))
        mapdata = get_object_or_404(MapData, page=page)
        return mapdata

    def get_object_date(self):
        return self.object.history.most_recent().history_info.date

    def get_context_data(self, **kwargs):
        context = super(MapDetailView, self).get_context_data(**kwargs)
        context['date'] = self.get_object_date()

        context['page'] = self.object.page
        context['map'] = InfoMap([(self.object.geom, self.object.page.name)],
                                 options=OLWIDGET_OPTIONS)
        return context


class MapVersionDetailView(MapDetailView):
    template_name = 'maps/mapdata_detail.html'
    context_object_name = 'mapdata'

    def get_object(self):
        mapdata = super(MapVersionDetailView, self).get_object()
        self.page = mapdata.page
        return mapdata.history.as_of(version=int(self.kwargs['version']))

    def get_object_date(self):
        return self.object.history_info.date

    def get_context_data(self, **kwargs):
        context = super(MapVersionDetailView, self).get_context_data(**kwargs)
        context['show_revision'] = True
        return context


class MapUpdateView(CreateObjectMixin, UpdateView):
    model = MapData
    form_class = MapForm

    def get_object(self):
        page_slug = self.kwargs.get('slug')
        page = Page.objects.get(slug=slugify(page_slug))
        mapdatas = MapData.objects.filter(page=page)
        if mapdatas:
            return mapdatas[0]
        return MapData(page=page)

    def get_success_url(self):
        return reverse('show-mapdata', args=[self.object.page.pretty_slug])


class MapDeleteView(MapDetailView, DeleteView):
    model = MapData
    context_object_name = 'mapdata'

    def get_success_url(self):
        # Redirect back to the map.
        return reverse('show-mapdata', args=[self.kwargs.get('slug')])


class MapRevertView(MapVersionDetailView, RevertView):
    model = MapData
    context_object_name = 'mapdata'
    template_name = 'maps/mapdata_confirm_revert.html'

    def get_success_url(self):
        # Redirect back to the map.
        return reverse('show-mapdata', args=[self.kwargs.get('slug')])

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        context['show_revision'] = True
        context['page'] = self.object.page
        context['map'] = InfoMap([(self.object.geom, self.object.page.name)],
                                 options=OLWIDGET_OPTIONS)
        context['date'] = self.object.history_info.date
        return context


class MapHistoryView(HistoryView):
    def get_queryset(self):
        page = Page.objects.get(slug=slugify(self.kwargs['slug']))
        self.mapdata = get_object_or_404(MapData, page=page)
        return self.mapdata.history.all()

    def get_context_data(self, **kwargs):
        context = super(MapHistoryView, self).get_context_data(**kwargs)
        context['mapdata'] = self.mapdata
        return context


class MapCompareView(diff.views.CompareView):
    model = MapData

    def get_object(self):
        page = Page.objects.get(slug=slugify(self.kwargs.get('slug')))
        return get_object_or_404(MapData, page=page)
