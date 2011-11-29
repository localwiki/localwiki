from dateutil.parser import parse as dateparser

from django.views.generic import DetailView, ListView
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.db.models import Q

from django.views.generic.list import BaseListView
from olwidget import utils
from olwidget.widgets import InfoMap as OLInfoMap
from django.contrib.gis.geos.polygon import Polygon
from django.utils.safestring import mark_safe

from versionutils import diff
from utils.views import Custom404Mixin, CreateObjectMixin, JSONResponseMixin
from versionutils.versioning.views import DeleteView, UpdateView
from versionutils.versioning.views import RevertView, VersionsList
from pages.models import Page
from pages.models import slugify

from widgets import InfoMap
from models import MapData
from forms import MapForm


class MapDetailView(Custom404Mixin, DetailView):
    model = MapData

    def handler404(self, request, *args, **kwargs):
        page_slug = kwargs.get('slug')
        try:
            page = Page.objects.get(slug=slugify(page_slug))
        except Page.DoesNotExist:
            page = Page(slug=slugify(page_slug))
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
        return self.object.versions.most_recent().version_info.date

    def get_context_data(self, **kwargs):
        context = super(MapDetailView, self).get_context_data(**kwargs)

        context['date'] = self.get_object_date()
        context['map'] = InfoMap([(self.object.geom, self.object.page.name)])
        return context


def filter_by_bounds(queryset, bbox):
    return queryset.filter(Q(points__intersects=bbox)
                         | Q(lines__intersects=bbox)
                         | Q(polys__intersects=bbox))


def filter_by_zoom(queryset, zoom):
    if zoom < 14:
        # exclude points
        queryset = queryset.exclude(Q(lines=None) & Q(polys=None))
    min_length = 100 * pow(2, 0 - zoom)
    queryset = queryset.exclude(Q(points=None) & Q(length__lt=min_length))
    return queryset


def popup_html(map_data):
    page = map_data.page
    return mark_safe('<a href="%s">%s</a>' %
                     (page.get_absolute_url(), page.name))


class MapGlobalView(ListView):
    model = MapData
    template_name = 'maps/mapdata_list.html'

    def get_queryset(self):
        queryset = super(MapGlobalView, self).get_queryset()
        # We order by -length so that the geometries are in that
        # order when rendered by OpenLayers -- this creates the
        # correct stacking order.
        return filter_by_zoom(queryset, 12).order_by('-length')

    def get_context_data(self, **kwargs):
        context = super(MapGlobalView, self).get_context_data(**kwargs)
        map_objects = [(obj.geom, popup_html(obj)) for obj in self.object_list]
        context['map'] = InfoMap(map_objects, options={
            'dynamic': True, 'zoomToDataExtent': False})
        context['dynamic_map'] = True
        return context


class MapAllObjectsAsPointsView(MapGlobalView):
    """
    Like MapGlobalView, but return all objects as points and do not filter by
    zoom.
    """
    def get_queryset(self):
        return super(MapGlobalView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(MapGlobalView, self).get_context_data(**kwargs)
        map_objects = [
            (obj.geom.centroid, popup_html(obj))
            for obj in self.object_list
        ]
        context['map'] = InfoMap(map_objects, options={
            'dynamic': False, 'zoomToDataExtent': False})
        context['dynamic_map'] = False
        return context


class MapObjectsForBounds(JSONResponseMixin, BaseListView):
    model = MapData

    def get_queryset(self):
        queryset = MapData.objects.all()
        bbox = self.request.GET.get('bbox', None)
        if bbox:
            bbox = Polygon.from_bbox([float(x) for x in bbox.split(',')])
            queryset = filter_by_bounds(queryset, bbox)
        zoom = self.request.GET.get('zoom', None)
        if zoom:
            # We order by -length so that the geometries are in that
            # order when rendered by OpenLayers -- this creates the
            # correct stacking order.
            queryset = filter_by_zoom(queryset, int(zoom)).order_by('-length')
        return queryset

    def get_context_data(self, **kwargs):
        map_objects = [(obj.geom, popup_html(obj)) for obj in self.object_list]
        return self.objects_to_wkt(map_objects)

    def objects_to_wkt(self, info):
        return [[utils.get_ewkt(geom), attr] for geom, attr in info]


class MapVersionDetailView(MapDetailView):
    template_name = 'maps/mapdata_version_detail.html'
    context_object_name = 'mapdata'

    def get_object(self):
        page = Page(slug=slugify(self.kwargs['slug']))  # A dummy page object.
        latest_page = page.versions.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name
        self.page = page

        mapdata = MapData(page=page)
        version = self.kwargs.get('version')
        date = self.kwargs.get('date')
        if version:
            return mapdata.versions.as_of(version=int(version))
        if date:
            return mapdata.versions.as_of(date=dateparser(date))

    def get_object_date(self):
        return self.object.version_info.date

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
        context['map'] = InfoMap([(self.object.geom, self.object.page.name)])
        context['date'] = self.object.version_info.date
        return context


class MapVersionsList(VersionsList):
    def get_queryset(self):
        page = Page(slug=slugify(self.kwargs['slug']))  # A dummy page object.
        latest_page = page.versions.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name

        self.mapdata = MapData(page=page)
        return self.mapdata.versions.all()

    def get_context_data(self, **kwargs):
        context = super(MapVersionsList, self).get_context_data(**kwargs)
        context['mapdata'] = self.mapdata
        return context


class MapCompareView(diff.views.CompareView):
    model = MapData

    def get_object(self):
        page = Page(slug=slugify(self.kwargs['slug']))  # A dummy page object.
        latest_page = page.versions.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name

        return MapData(page=page)

    def get_context_data(self, **kwargs):
        # Send this in directly because we've wrapped InfoMap.
        context = super(MapCompareView, self).get_context_data(**kwargs)
        # We subclassed olwidget.widget.InfoMap. We want to combine both
        # their media here to ensure we display more than one layer
        # correctly.
        context['map_diff_media'] = InfoMap([]).media + OLInfoMap([]).media
        return context
