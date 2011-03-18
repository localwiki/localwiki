from copy import copy
from django.views.generic import DetailView, UpdateView, ListView
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse

from olwidget.widgets import InfoMap

from versionutils import diff
from utils.views import Custom404Mixin, CreateObjectMixin
from pages.models import Page
from pages.models import slugify

from models import MapData
from forms import MapForm


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

    def get_context_data(self, **kwargs):
        context = super(MapDetailView, self).get_context_data(**kwargs)
        context['page'] = self.object.page
        context['map'] = InfoMap([(self.object.geom, self.object.page.name)])
        context['date'] = self.object.history.most_recent().history_info.date
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
        return reverse('show-page-map', args=[self.object.page.pretty_slug])


class MapHistoryView(ListView):
    context_object_name = "version_list"
    template_name = "maps/mapdata_history.html"

    def get_queryset(self):
        page = Page.objects.get(slug=slugify(self.kwargs['slug']))
        self.mapdata = get_object_or_404(MapData, page=page)
        return self.mapdata.history.all()

    def get_context_data(self, **kwargs):
        context = super(MapHistoryView, self).get_context_data(**kwargs)
        context['mapdata'] = self.mapdata
        return context


class MapVersionDetailView(MapDetailView):
    template_name = 'maps/mapdata_detail.html'
    context_object_name = 'mapdata'

    def get_object(self):
        mapdata = super(MapVersionDetailView, self).get_object()
        self.page = mapdata.page
        return mapdata.history.as_of(version=int(self.kwargs['version']))

    def get_context_data(self, **kwargs):
        # we don't want PageDetailView's context, skip to DetailView's
        context = super(DetailView, self).get_context_data(**kwargs)

        context['show_revision'] = True
        context['page'] = self.page
        context['map'] = InfoMap([(self.object.geom, self.object.page.name)])
        context['date'] = self.object.history_info.date
        return context


class MapCompareView(diff.views.CompareView):
    model = MapData

    def get_context_data(self, **kwargs):
        context = super(MapCompareView, self).get_context_data(**kwargs)
        context['map_media'] = InfoMap([]).media
        return context

    def get_object(self):
        page = Page.objects.get(slug=slugify(self.kwargs.get('slug')))
        return get_object_or_404(MapData, page=page)
