import copy
from PIL import Image
from cStringIO import StringIO

from django.views.generic import View 
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.files.base import ContentFile
from django.conf import settings

from pages.models import Page
from pages.views import PageDetailView
from maps.models import MapData
from maps.widgets import InfoMap, map_options_for_region
from regions.views import RegionMixin, RegionAdminRequired, TemplateView, region_404_response
from regions.models import Region
from localwiki.utils.views import Custom404Mixin

from .models import FrontPage


class FrontPageView(Custom404Mixin, TemplateView):
    template_name = 'frontpage/base.html'

    def get(self, *args, **kwargs):
        # If there's no FrontPage defined, let's send the "Front Page" Page object.
        region = self.get_region()
        if not FrontPage.objects.filter(region=region).exists() or region.regionsettings.is_meta_region:
            page_view = PageDetailView()
            page_view.kwargs = {'slug': 'Front Page', 'region': self.get_region().slug}
            page_view.request = self.request
            return page_view.get(*args, **kwargs)
        return super(FrontPageView, self).get(*args, **kwargs)

    def get_map_objects(self):
        centroids = MapData.objects.filter(
            region=self.get_region()).centroid().values('centroid')
        return [(g['centroid'], '') for g in centroids]

    def get_map(self, cover=False):
        olwidget_options = copy.deepcopy(getattr(settings,
            'OLWIDGET_DEFAULT_OPTIONS', {}))
        map_opts = olwidget_options.get('map_options', {})
        olwidget_options.update(map_options_for_region(self.get_region()))
        map_controls = map_opts.get('controls', [])
        if 'PanZoom' in map_controls:
            map_controls.remove('PanZoom')
        if 'PanZoomBar' in map_controls:
            map_controls.remove('PanZoomBar')
        if 'KeyboardDefaults' in map_controls:
            map_controls.remove('KeyboardDefaults')
        if 'Navigation' in map_controls:
            map_controls.remove('Navigation')
        if not cover:
            olwidget_options['map_div_class'] = 'mapwidget small'
        olwidget_options['map_options'] = map_opts
        olwidget_options['zoomToDataExtent'] = False
        olwidget_options['cluster'] = True
        if cover:
            return InfoMap([], options=olwidget_options)
        else:
            return InfoMap(self.get_map_objects(), options=olwidget_options)

    def get_pages_for_cards(self):
        qs = Page.objects.filter(region=self.get_region())

        # Exclude meta stuff
        qs = qs.exclude(slug__startswith='templates/')
        qs = qs.exclude(slug='templates')
        qs = qs.exclude(slug='front page')

        # Exclude ones with empty scores
        qs = qs.exclude(score=None)

        qs = qs.defer('content').select_related('region').order_by('-score__score', '?')

        # Just grab 5 items
        return qs[:5]

    def get_context_data(self, *args, **kwargs):
        context = super(FrontPageView, self).get_context_data() 

        context['frontpage'] = FrontPage.objects.get(region=self.get_region())
        context['map'] = self.get_map()
        context['cover_map'] = self.get_map(cover=True)
        context['pages_for_cards'] = self.get_pages_for_cards()
        if Page.objects.filter(name="Front Page", region=self.get_region()).exists():
            context['page'] = Page.objects.get(name="Front Page", region=self.get_region())
        else:
            context['page'] = Page(name="Front Page", region=self.get_region())
        return context

    def handler404(self, request, *args, **kwargs):
        return region_404_response(request, kwargs.get('region'))


class CoverUploadView(RegionMixin, RegionAdminRequired, View):
    def post(self, *args, **kwargs):

        photo = self.request.FILES.get('file')

        client_cover_w = int(self.request.POST.get('client_w'))
        client_cover_h = int(self.request.POST.get('client_h'))
        client_position_x = abs(int(self.request.POST.get('position_x')))
        client_position_y = abs(int(self.request.POST.get('position_y')))
        axis = self.request.POST.get('cover_position_axis')

        if client_cover_w <= 0 or client_cover_h <= 0:
            raise Exception

        im = Image.open(photo)
        exact_w, exact_h = im.size

        if axis == 'y':
            scale = (exact_w * 1.0)/ client_cover_w
            position_y = scale * client_position_y
            exact_cover_h = client_cover_h * scale

            left = 0
            upper = int(position_y)
            right = int(exact_w)
            lower = int(position_y + exact_cover_h)
            bbox = (left, upper, right, lower)
        else:
            scale = (exact_h * 1.0)/ client_cover_h
            position_x = scale * client_position_x
            exact_cover_w = client_cover_w * scale

            left = int(position_x)
            upper = 0
            right = int(position_x + exact_cover_w)
            lower = exact_h
            bbox = (left, upper, right, lower)

        cropped = im.crop(bbox)
        cropped_s = StringIO()
        cropped.save(cropped_s, "JPEG", quality=90)
        cropped_f = ContentFile(cropped_s.getvalue())

        frontpage = FrontPage.objects.get(region=self.get_region())
        frontpage.cover_photo_full = photo
        frontpage.cover_photo.save(photo.name, cropped_f)
        frontpage.cover_photo_crop_bbox_left = left
        frontpage.cover_photo_crop_bbox_upper = upper
        frontpage.cover_photo_crop_bbox_right = right
        frontpage.cover_photo_crop_bbox_lower = lower
        frontpage.save()

        messages.add_message(self.request, messages.SUCCESS, _("Cover photo updated!"))
                
        return HttpResponseRedirect(
            reverse('frontpage', kwargs={'region': self.get_region().slug}))
