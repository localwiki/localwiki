from django.core.urlresolvers import reverse
from django.views.generic import TemplateView as DjangoTemplateView
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.conf import settings

from localwiki.utils.views import CreateObjectMixin

from models import Region, slugify
from forms import RegionForm


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


class RegionListView(ListView):
    model = Region
    context_object_name = 'regions'

    def get_queryset(self):
        return Region.objects.all().exclude(slug=settings.MAIN_REGION).order_by('full_name')


class MainPageView(RegionListView):
    template_name = 'regions/main.html'


class RegionCreateView(CreateView):
    model = Region
    form_class = RegionForm

    def get_success_url(self):
        return reverse('frontpage', kwargs={'region': self.object.slug})

    def get_form_kwargs(self):
        kwargs = super(RegionCreateView, self).get_form_kwargs()
        if kwargs.get('data'):
            kwargs['data'] = kwargs['data'].copy()  # otherwise immutable
            kwargs['data']['slug'] = slugify(kwargs['data']['slug'])
        return kwargs

    def form_valid(self, form):
        response = super(RegionCreateView, self).form_valid(form)
        # Create the initial pages, etc in the region
        self.object.populate_region()
        return response
