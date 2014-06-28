import copy

from django.conf.urls import *
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from haystack.views import SearchView
from haystack.forms import SearchForm as DefaultSearchForm

from pages.models import Page, slugify
from maps.models import MapData
from maps.widgets import InfoMap, map_options_for_region
from regions.views import RegionMixin


class WithMapSearchView(SearchView):
    def get_map(self):
        (paginator, page) = self.build_page()
        result_pks = [p.pk for p in page.object_list if p]
        maps = MapData.objects.filter(page__pk__in=result_pks)
        if not maps:
            return None
        widget_options = copy.deepcopy(getattr(settings,
            'OLWIDGET_DEFAULT_OPTIONS', {}))
        map_opts = widget_options.get('map_options', {})
        map_controls = map_opts.get('controls', [])
        # Remove the PanZoom.
        if 'PanZoomBar' in map_controls:
            map_controls.remove('PanZoomBar')
        if 'PanZoom' in map_controls:
            map_controls.remove('PanZoom')
        # Remove the Keyboard scrolling behavior.
        if 'KeyboardDefaults' in map_controls:
            map_controls.remove('KeyboardDefaults')
        widget_options['map_options'] = map_opts
        widget_options['map_div_class'] = 'mapwidget small'
        map = InfoMap([(obj.geom, popup_html(obj)) for obj in maps],
            options=widget_options)
        return map

    def extra_context(self):
        context = super(WithMapSearchView, self).extra_context()
        context['query_slug'] = Page(name=self.query).pretty_slug
        context['keywords'] = self.query.split()
        context['map'] = self.get_map()
        return context


class GlobalSearchView(WithMapSearchView):
    template = 'search/global_search.html'


class CreatePageSearchView(WithMapSearchView, RegionMixin):
    def __call__(self, request, region=''):
        from regions.models import Region
        self.region = self.get_region(request=request, kwargs={'region': region})
        return super(CreatePageSearchView, self).__call__(request)

    def build_form(self, *args, **kwargs):
        form = super(CreatePageSearchView, self).build_form(*args, **kwargs)
        form.region = self.region
        return form

    def extra_context(self):
        context = super(CreatePageSearchView, self).extra_context()
        context['allow_page_creation'] = not Page.objects.filter(
            slug=slugify(self.query), region=self.region).exists()
        context['region'] = self.region
        return context


def popup_html(map_data):
    page = map_data.page
    return mark_safe('<a href="%s">%s</a>' %
                     (page.get_absolute_url(), page.name))


class SearchForm(DefaultSearchForm):
    def search(self):
        sqs = super(SearchForm, self).search()
        cleaned_data = getattr(self, 'cleaned_data', {})
        keywords = cleaned_data.get('q', '').split()
        if not keywords:
            return sqs
        # we do __in because we want partial matches, not just exact ones.
        # And by default, Haystack only searches the `document` field, so
        # we need this to activate the boosts.
        return sqs.filter_or(full_name__in=keywords).\
            filter_or(slug__in=keywords).filter_or(name__in=keywords).\
            filter_or(tags__in=keywords)


class InRegionSearchForm(DefaultSearchForm):
    def search(self):
        sqs = super(InRegionSearchForm, self).search()
        cleaned_data = getattr(self, 'cleaned_data', {})
        keywords = cleaned_data.get('q', '').split()
        if not keywords:
            return sqs
        # we do __in because we want partial matches, not just exact ones.
        # And by default, Haystack only searches the `document` field, so
        # we need this to activate the boosts.
        return sqs.filter_or(name__in=keywords).filter_or(tags__in=keywords).filter_and(region_id=self.region.id)


def search_view_factory(view_class=SearchView, *args, **kwargs):
    def search_view(request, **kwargs2):
        return view_class(*args, **kwargs)(request, **kwargs2)
    return search_view

haystack_search = search_view_factory(
    view_class=CreatePageSearchView,
    form_class=InRegionSearchForm
) 

global_search = search_view_factory(
    view_class=GlobalSearchView,
    form_class=SearchForm
)

urlpatterns_no_region = patterns('',
    url(r'^_rsearch/(?P<region>[^/]+)?/?$', haystack_search , name='haystack_search'),
)

urlpatterns = urlpatterns_no_region + patterns('',
    url(r'^_search/$', global_search, name='global_search'),
)
