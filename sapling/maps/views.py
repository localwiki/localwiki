from dateutil.parser import parse as dateparser

from django.views.generic import DetailView
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.conf import settings

from olwidget.widgets import InfoMap

from versionutils import diff
from utils.views import Custom404Mixin, CreateObjectMixin
from versionutils.versioning.views import DeleteView, UpdateView
from versionutils.versioning.views import RevertView, HistoryList
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
        mapdata = MapData(page=page)
        return HttpResponseNotFound(
            direct_to_template(request, 'maps/mapdata_new.html',
                {'page': page, 'mapdata': mapdata})
        )

    def get_object(self):
        page_slug = self.kwargs.get('slug')
        page = get_object_or_404(Page, slug=slugify(page_slug))
        mapdata = get_object_or_404(MapData, page=page)
        return mapdata

    def get_object_date(self):
        return self.object.history.most_recent().history_info.date

    def get_context_data(self, **kwargs):
        context = super(MapDetailView, self).get_context_data(**kwargs)

        context['date'] = self.get_object_date()
        context['map'] = InfoMap([(self.object.geom, self.object.page.name)],
                                 options=OLWIDGET_OPTIONS)
        return context


class MapVersionDetailView(MapDetailView):
    template_name = 'maps/mapdata_detail.html'
    context_object_name = 'mapdata'

    def get_object(self):
        page = Page(slug=slugify(self.kwargs['slug']))  # A dummy page object.
        latest_page = page.history.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name
        self.page = page

        mapdata = MapData(page=page)
        version = self.kwargs.get('version')
        date = self.kwargs.get('date')
        if version:
            return mapdata.history.as_of(version=int(version))
        if date:
            return mapdata.history.as_of(date=dateparser(date))

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
        return reverse('maps:show', args=[self.object.page.pretty_slug])


class MapDeleteView(MapDetailView, DeleteView):
    model = MapData
    context_object_name = 'mapdata'

    def get_success_url(self):
        # Redirect back to the map.
        return reverse('maps:show', args=[self.kwargs.get('slug')])


class MapRevertView(MapVersionDetailView, RevertView):
    model = MapData
    context_object_name = 'mapdata'
    template_name = 'maps/mapdata_confirm_revert.html'

    def get_success_url(self):
        # Redirect back to the map.
        return reverse('maps:show', args=[self.kwargs.get('slug')])

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        context['show_revision'] = True
        context['map'] = InfoMap([(self.object.geom, self.object.page.name)],
                                 options=OLWIDGET_OPTIONS)
        context['date'] = self.object.history_info.date
        return context


class MapHistoryList(HistoryList):
    def get_queryset(self):
        page = Page(slug=slugify(self.kwargs['slug']))  # A dummy page object.
        latest_page = page.history.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name

        self.mapdata = MapData(page=page)
        return self.mapdata.history.all()

    def get_context_data(self, **kwargs):
        context = super(MapHistoryList, self).get_context_data(**kwargs)
        context['mapdata'] = self.mapdata
        return context


class MapCompareView(diff.views.CompareView):
    model = MapData

    def get_object(self):
        page = Page(slug=slugify(self.kwargs['slug']))  # A dummy page object.
        latest_page = page.history.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name

        return MapData(page=page)
