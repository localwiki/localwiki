import copy
from dateutil.parser import parse as dateparser
from operator import attrgetter

from django.conf import settings
from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.db.models import Q
from django.db import IntegrityError
from django.views.generic.list import BaseListView
from olwidget.widgets import InfoMap as OLInfoMap
from django.contrib.gis.geos.polygon import Polygon
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext as _
from django.contrib.gis.measure import D
from django.utils.safestring import mark_safe
from django.utils.html import escape

from versionutils import diff
from utils.views import (Custom404Mixin, CreateObjectMixin, JSONResponseMixin,
    JSONView, PermissionRequiredMixin, DeleteView, RevertView)
from utils.urlresolvers import reverse
from versionutils.versioning.views import UpdateView
from versionutils.versioning.views import VersionsList
from pages.models import Page, slugify, name_to_url, page_url
from regions.views import RegionMixin, region_404_response
from regions.models import Region
from users.views import AddContributorsMixin

from .widgets import InfoMap, map_options_for_region
from .models import MapData
from .forms import MapForm
from .osm import get_osm_geom


class MapDetailView(Custom404Mixin, AddContributorsMixin, RegionMixin, DetailView):
    model = MapData

    def handler404(self, request, *args, **kwargs):
        page_slug = kwargs.get('slug')
        try:
            region = self.get_region(request=request, kwargs=kwargs)
        except Http404:
            return region_404_response(request, kwargs['region']) 

        try:
            page = Page.objects.get(slug=slugify(page_slug), region=region)
        except Page.DoesNotExist:
            page = Page(slug=slugify(page_slug), region=region)

        mapdata = MapData(page=page, region=region)
        return HttpResponseNotFound(
            render(request, 'maps/mapdata_new.html',
                {'page': page, 'mapdata': mapdata})
        )

    def get_object(self):
        page_slug = self.kwargs.get('slug')
        region = self.get_region()
        page = get_object_or_404(Page, slug=slugify(page_slug), region=region)
        mapdata = get_object_or_404(MapData, page=page, region=region)
        return mapdata

    def get_object_date(self):
        return self.object.versions.most_recent().version_info.date

    def get_context_data(self, **kwargs):
        context = super(MapDetailView, self).get_context_data(**kwargs)

        options = map_options_for_region(self.get_region())
        options['permalink'] = True
        context['date'] = self.get_object_date()
        context['map'] = InfoMap([(self.object.geom, self.object.page.name)],
            options=options)
        return context


def filter_by_bounds(queryset, bbox):
    return queryset.filter(Q(points__intersects=bbox)
                         | Q(lines__within=bbox)
                         | Q(polys__intersects=bbox))


def filter_by_zoom(queryset, zoom):
    if zoom < 14:
        # If 5 or more polygons, let's hide the points
        if queryset.filter(polys__isnull=False).count() >= 5:
            # exclude points
            queryset = queryset.exclude(Q(lines=None) & Q(polys=None))
    min_length = 100 * pow(2, 0 - zoom)
    queryset = queryset.exclude(Q(points=None) & Q(length__lt=min_length))
    return queryset


def popup_html(mapdata=None, pagename=None):
    if mapdata:
        pagename = mapdata.page.name
    url = page_url(pagename, mapdata.region)
    return mark_safe('<a href="%s">%s</a>' % (url, pagename))


class MapGlobalView(RegionMixin, ListView):
    model = MapData
    template_name = 'maps/mapdata_list.html'
    dynamic = True
    zoom_to_data = False
    filter_by_zoom = True
    permalink = True

    def get_queryset(self):
        queryset = super(MapGlobalView, self).get_queryset()
        # XXX TODO TEMPORARY HACK
        queryset = queryset.exclude(page__pagetagset__tags__slug='zipcode')
        queryset = queryset.exclude(page__pagetagset__tags__slug='supervisorialdistrict')
        if not filter_by_zoom:
            return queryset
        # We order by -length so that the geometries are in that
        # order when rendered by OpenLayers -- this creates the
        # correct stacking order.
        return filter_by_zoom(queryset, 12).order_by('-length')

    def get_context_data(self, **kwargs):
        context = super(MapGlobalView, self).get_context_data(**kwargs)
        context['map'] = self.get_map()
        context['dynamic_map'] = self.dynamic
        return context

    def get_map_objects(self):
        return [(obj.geom, popup_html(obj)) for obj in self.object_list]

    def get_map(self):
        map_objects = self.get_map_objects()
        options = map_options_for_region(self.get_region())
        options.update({
            'dynamic': self.dynamic,
            'zoomToDataExtent': self.zoom_to_data,
            'permalink': self.permalink,
            'cluster': True
        })
        return InfoMap(map_objects, options=options)


class MapAllObjectsAsPointsView(MapGlobalView):
    """
    Like MapGlobalView, but return all objects as points and do not filter by
    zoom.
    """
    dynamic = False
    zoom_to_data = False
    filter_by_zoom = False

    def get_map_objects(self):
        return [(obj.geom.centroid, popup_html(obj))
                for obj in self.object_list
               ]


class EverythingEverywhereAsPointsView(MapAllObjectsAsPointsView):
    """
    All objects across all regions as points.
    """
    def get_queryset(self):
        return MapData.objects.all()


class MapForTag(MapGlobalView):
    """
    All objects whose pages have a particular tag.
    """
    dynamic = False
    zoom_to_data = True

    def get_queryset(self):
        import tags.models as tags

        qs = super(MapGlobalView, self).get_queryset()
        region = self.get_region()
        self.tag = tags.Tag.objects.get(
            slug=tags.slugify(self.kwargs['tag']),
            region=region
        )
        tagsets = tags.PageTagSet.objects.filter(tags=self.tag, region=region)
        pages = Page.objects.filter(pagetagset__in=tagsets, region=region)
        return MapData.objects.filter(page__in=pages).order_by('-length')

    def get_map_title(self):
        region = self.get_region()
        d = {
            'map_url': reverse('maps:global', kwargs={'region' : region.slug}),
            'tag_url': reverse('tags:list', kwargs={'region': region.slug}),
            'page_tag_url': reverse('tags:tagged',
                kwargs={'slug': self.tag.slug, 'region': region.slug}),
            'tag_name': escape(self.tag.name)
        }
        return (
            '<a href="%(map_url)s">Map</a> / '
            '<a href="%(tag_url)s">Tags</a> / '
            '<a href="%(page_tag_url)s">%(tag_name)s</a>' % d)

    def get_context_data(self, **kwargs):
        context = super(MapForTag, self).get_context_data(**kwargs)
        context['map_title'] = self.get_map_title()
        return context


class MapObjectsForBounds(JSONResponseMixin, RegionMixin, BaseListView):
    model = MapData

    def get_queryset(self):
        queryset = MapData.objects.filter(region=self.get_region())
        # XXX TODO TEMPORARY HACK
        queryset = queryset.exclude(page__pagetagset__tags__slug='zipcode')
        queryset = queryset.exclude(page__pagetagset__tags__slug='supervisorialdistrict')
        bbox = self.request.GET.get('bbox', None)
        if bbox:
            bbox = Polygon.from_bbox([float(x) for x in bbox.split(',')])
            queryset = filter_by_bounds(queryset, bbox)
        zoom = self.request.GET.get('zoom', None)
        if zoom:
            # We order by -length so that the geometries are in that
            # order when rendered by OpenLayers. This creates the
            # correct stacking order.
            queryset = filter_by_zoom(queryset, int(zoom)).order_by('-length')
        return queryset.select_related('page')

    def get_context_data(self, **kwargs):
        objs = self.object_list.values('geom', 'page__name')
        region = self.get_region()
        map_objects = [
            (o['geom'].ewkt, o['page__name'], page_url(o['page__name'], region))
            for o in objs
        ]
        return map_objects


class OSMGeometryLookup(RegionMixin, JSONView):
    def get_context_data(self, **kwargs):
        display_name = self.request.GET.get('display_name')
        osm_id = int(self.request.GET.get('osm_id'))
        osm_type = self.request.GET.get('osm_type')
        return {'geom': get_osm_geom(osm_id, osm_type, display_name, self.get_region()).ewkt}


class MapVersionDetailView(MapDetailView):
    template_name = 'maps/mapdata_version_detail.html'
    context_object_name = 'mapdata'

    def get_object(self):
        region = self.get_region()
        # A dummy page object.
        page = Page(
            slug=slugify(self.kwargs['slug']),
            region=region
        )
        latest_page = page.versions.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name
        self.page = page

        mapdata = MapData(page=page, region=region)
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


class MapUpdateView(PermissionRequiredMixin, CreateObjectMixin, RegionMixin, UpdateView):
    model = MapData
    form_class = MapForm
    # Tie map permissions to pages, for now.
    permission = 'pages.change_page'

    def get_object(self):
        page_slug = self.kwargs.get('slug')
        region = self.get_region()
        page = Page.objects.get(slug=slugify(page_slug), region=region)
        mapdatas = MapData.objects.filter(page=page, region=region)
        if mapdatas:
            return mapdatas[0]
        return MapData(page=page, region=region)

    def get_protected_object(self):
        return self.object.page

    def get_context_data(self, *args, **kwargs):
        context = super(MapUpdateView, self).get_context_data(*args, **kwargs)
        # Default to the region's defined map settings.
        # TODO: make this less hacky
        context['form'].fields['geom'].widget.options.update(map_options_for_region(self.get_region()))
        return context

    def get_success_url(self):
        return reverse('maps:show',
            kwargs={'region': self.object.region.slug, 'slug': self.object.page.pretty_slug})


class MapCreateWithoutPageView(MapUpdateView):
    def _get_or_create_page(self):
        pagename = self.request.GET.get('pagename')
        region = self.get_region()
        has_page = Page.objects.filter(slug=slugify(pagename), region=region)
        if has_page:
            page = has_page[0]
        else:
            content = _('<p>What do you know about %s?</p>') % pagename
            page = Page(slug=slugify(pagename), name=pagename, content=content, region=region)
        return page

    def get_object(self):
        page = self._get_or_create_page()
        region = self.get_region()
        if MapData.objects.filter(page=page, region=region).exists():
            return MapData.objects.get(page=page, region=region)
        return MapData(page=page, region=region)

    def form_valid(self, form):
        page = self._get_or_create_page()
        page.save(comment=form.get_save_comment())
        self.object.page = page
        return super(MapCreateWithoutPageView, self).form_valid(form)

    def success_msg(self):
        return (
            _('Map saved! You should probably go <a href="%s">edit the page that was created</a>, too.') %
            reverse('pages:edit', kwargs={'region': self.get_region().slug, 'slug': self.object.page.name})
        )

    def get_context_data(self, *args, **kwargs):
        context = super(MapCreateWithoutPageView, self).get_context_data(*args, **kwargs)
        # TODO: make this less hacky
        context['form'].fields['geom'].widget.options.update({'permalink': True})
        return context

    def get_map(self):
        map_objects = self.get_map_objects()
        options = map_options_for_region(self.get_region())
        options.update({
            'dynamic': self.dynamic,
            'zoomToDataExtent': self.zoom_to_data,
            'permalink': self.permalink,
            'cluster': True
        })
        return InfoMap(map_objects, options=options)


class MapDeleteView(PermissionRequiredMixin, MapDetailView, DeleteView):
    model = MapData
    context_object_name = 'mapdata'
    # Tie map permissions to pages, for now.
    permission = 'pages.delete_page'

    def get_success_url(self):
        # Redirect back to the map.
        return reverse('maps:show',
            kwargs={'region': self.get_region().slug, 'slug': self.kwargs.get('slug')})

    def get_protected_object(self):
        return self.object.page


class MapRevertView(MapVersionDetailView, RevertView):
    model = MapData
    context_object_name = 'mapdata'
    template_name = 'maps/mapdata_confirm_revert.html'
    # Tie map permissions to pages, for now.
    permission = 'pages.change_page'

    def get_success_url(self):
        # Redirect back to the map.
        return reverse('maps:show',
            kwargs={'region': self.get_region().slug, 'slug': self.kwargs.get('slug')})

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        options = map_options_for_region(self.get_region())
        context['show_revision'] = True
        context['map'] = InfoMap([(self.object.geom, self.object.page.name)], options=options)
        context['date'] = self.object.version_info.date
        return context

    def get_protected_object(self):
        return self.object.page


class MapVersionsList(RegionMixin, VersionsList):
    def get_queryset(self):
        region = self.get_region()
        # A dummy page object.
        page = Page(slug=slugify(self.kwargs['slug']), region=region)
        latest_page = page.versions.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name

        self.mapdata = MapData(page=page, region=region)
        return self.mapdata.versions.all()

    def get_context_data(self, **kwargs):
        context = super(MapVersionsList, self).get_context_data(**kwargs)
        context['mapdata'] = self.mapdata
        return context


class MapCompareView(RegionMixin, diff.views.CompareView):
    model = MapData

    def get_object(self):
        region = self.get_region()
        # A dummy page object.
        page = Page(slug=slugify(self.kwargs['slug']), region=region)
        latest_page = page.versions.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name

        return MapData(page=page, region=region)

    def get_context_data(self, **kwargs):
        # Send this in directly because we've wrapped InfoMap.
        context = super(MapCompareView, self).get_context_data(**kwargs)
        # We subclassed olwidget.widget.InfoMap. We want to combine both
        # their media here to ensure we display more than one layer
        # correctly.
        context['map_diff_media'] = InfoMap([]).media + OLInfoMap([]).media
        return context


class MapNearbyView(RegionMixin, ListView):
    model = MapData
    template_name = 'maps/nearby_pages.html'
    context_object_name = 'nearby_maps'

    def get_queryset(self):
        if not self.request.GET.get('lat'):
            return None

        nearby_meters = 1000
        lat = float(self.request.GET.get('lat'))
        lng = float(self.request.GET.get('lng'))
        user_location = Point(lng, lat)

        points = MapData.objects.filter(points__distance_lte=(user_location, D(m=nearby_meters))).distance(user_location).order_by('distance')[:30]
        polys = MapData.objects.filter(polys__distance_lte=(user_location, D(m=nearby_meters))).distance(user_location).order_by('distance')[:30]
        lines = MapData.objects.filter(lines__distance_lte=(user_location, D(m=nearby_meters))).distance(user_location).order_by('distance')[:30]

        queryset = sorted(list(points)+list(polys)+list(lines), key=attrgetter('distance'))[:30]
        return queryset

    def get_context_data(self, *args, **kwargs):
        from maps.widgets import InfoMap
        context = super(MapNearbyView, self).get_context_data(*args, **kwargs)
        qs = self.get_queryset()
        if qs is None:
            context['no_location'] = True
            qs = []
        map_objects = [(obj.geom, popup_html(obj)) for obj in qs]

        # Remove the PanZoom on normal page views.
        olwidget_options = copy.deepcopy(getattr(settings,
            'OLWIDGET_DEFAULT_OPTIONS', {}))
        map_opts = olwidget_options.get('map_options', {})
        map_controls = map_opts.get('controls', [])
        if 'PanZoomBar' in map_controls:
            map_controls.remove('PanZoomBar')
        if 'PanZoom' in map_controls:
            map_controls.remove('PanZoom')
        if 'KeyboardDefaults' in map_controls:
            map_controls.remove('KeyboardDefaults')
        olwidget_options['map_options'] = map_opts
        olwidget_options['map_div_class'] = 'mapwidget small'
        context['map'] = InfoMap(
            map_objects,
            options=olwidget_options)
        return context
