from django.core.urlresolvers import reverse
from django.views.generic import TemplateView

from pages.models import Page, PageFile
from maps.models import MapData
from redirects.models import Redirect


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard_main.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['num_pages'] = len(Page.objects.all())
        context['num_files'] = len(PageFile.objects.all())
        context['num_maps'] = len(MapData.objects.all())
        context['num_redirects'] = len(Redirect.objects.all())

        return context
