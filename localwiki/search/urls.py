import copy

from django.conf.urls import *
from django.conf import settings
from django.utils.safestring import mark_safe

from haystack.views import SearchView
from haystack.forms import SearchForm as DefaultSearchForm

from pages.models import Page, slugify
from maps.models import MapData
from maps.widgets import InfoMap


class CreatePageSearchView(SearchView):
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
        # Remove the PanZoomBar.
        if 'PanZoomBar' in map_controls:
            map_controls.remove('PanZoomBar')
        # Remove the Keyboard scrolling behavior.
        if 'KeyboardDefaults' in map_controls:
            map_controls.remove('KeyboardDefaults')
        widget_options['map_options'] = map_opts
        widget_options['map_div_class'] = 'mapwidget small'
        map = InfoMap([(obj.geom, popup_html(obj)) for obj in maps],
            options=widget_options)
        return map

    def extra_context(self):
        context = super(CreatePageSearchView, self).extra_context()
        context['page_exists_for_query'] = Page.objects.filter(
            slug=slugify(self.query))
        context['query_slug'] = Page(name=self.query).pretty_slug
        context['keywords'] = self.query.split()
        context['map'] = self.get_map()
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
        # we do __in because we want partial matches, not just exact ones
        return sqs.filter_or(name__in=keywords).filter_or(tags__in=keywords)

urlpatterns = patterns('',
    url(r'^$', CreatePageSearchView(form_class=SearchForm),
        name='haystack_search'),
)
