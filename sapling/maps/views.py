from django.views.generic import DetailView, UpdateView, ListView
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse

from olwidget.widgets import InfoMap

from utils.views import Custom404Mixin, CreateObjectMixin
from models import MapData
from forms import MapForm
from pages.models import Page
from pages.models import slugify


# XXX
# add custom4040mixin thing
class MapDetailView(DetailView):
    model = MapData

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
        mapdata = get_object_or_404(MapData, page=page)
        return mapdata

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


# XXX
# TODO: refactor this out of here and out of pages.views
def compare(request, slug, version1=None, version2=None, **kwargs):
    versions = request.GET.getlist('version')
    if not versions:
        versions = [v for v in (version1, version2) if v]
    if not versions:
        return redirect(reverse('page-map-history', args=[slug]))
    page = Page.objects.get(slug=slugify(slug))
    mapdata = get_object_or_404(MapData, page=page)
    versions = [int(v) for v in versions]
    old = min(versions)
    new = max(versions)
    if len(versions) == 1:
        old = max(new - 1, 1)
    old_version = mapdata.history.as_of(version=old)
    new_version = mapdata.history.as_of(version=new)
    media = InfoMap([]).media
    context = {
        'old': old_version, 'new': new_version,
        'mapdata': mapdata, 'map_media': media,
    }
    return direct_to_template(request, 'maps/mapdata_diff.html', context)
