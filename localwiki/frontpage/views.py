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

from pages.views import PageDetailView
from pages.models import Page
from maps.widgets import InfoMap, map_options_for_region
from regions.views import RegionMixin
from regions.views import TemplateView

from models import FrontPage


class FrontPageView(TemplateView):
    template_name = 'frontpage/base.html'

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
        return InfoMap([], options=olwidget_options)

    def get_context_data(self, *args, **kwargs):
        context = super(FrontPageView, self).get_context_data() 
        # So that the Page can be edited if they want to replace
        # the auto-generated Front Page.
        context['frontpage'] = FrontPage.objects.get(region=self.get_region())
        context['map'] = self.get_map()
        context['cover_map'] = self.get_map(cover=True)
        context['random_pages'] = Page.objects.filter(region=self.get_region()).order_by('?')[:30]
        if Page.objects.filter(name="Front Page", region=self.get_region()).exists():
            context['page'] = Page.objects.get(name="Front Page", region=self.get_region())
        else:
            context['page'] = Page(name="Front Page", region=self.get_region())
        return context


class CoverUploadView(RegionMixin, View):
    def post(self, *args, **kwargs):

        photo = self.request.FILES.get('file')

        client_cover_w = int(self.request.POST.get('client_w'))
        client_cover_h = int(self.request.POST.get('client_h'))
        client_position_y = abs(int(self.request.POST.get('position_y')))

        if client_cover_w <= 0 or client_cover_h <= 0:
            raise Exception

        im = Image.open(photo)
        exact_w, exact_h = im.size
        scale = (exact_w * 1.0)/ client_cover_w
        position_y = scale * client_position_y
        exact_cover_h = client_cover_h * scale

        left = 0
        upper = int(position_y)
        right = int(exact_w)
        lower = int(position_y + exact_cover_h)
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
