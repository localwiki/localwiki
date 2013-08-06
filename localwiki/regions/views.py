from django.core.urlresolvers import reverse
from django.views.generic import TemplateView as DjangoTemplateView
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from utils.views import CreateObjectMixin

from models import Region, slugify


class RegionMixin(object):
    """
    Provides helpers to views that deal with Regions.
    """
    def get_region(self):
        """
        Returns the Region associated with this view.
        """
        return Region.objects.get(
            slug=slugify(self.kwargs.get('region')))

    def get_queryset(self):
        qs = super(RegionMixin, self).get_queryset()
        return qs.filter(region=self.get_region())

    def get_context_data(self, *args, **kwargs):
        context = super(RegionMixin, self).get_context_data(*args, **kwargs)
        context['region'] = self.get_region()
        return context


class TemplateView(RegionMixin, DjangoTemplateView):
    pass


class MainPageView(ListView):
    model = Region
    context_object_name = 'regions'
    queryset = Region.objects.all().order_by('full_name')


class RegionCreateView(CreateView):
    model = Region

    def get_success_url(self):
        return reverse('pages:frontpage', args=[self.object.slug])

