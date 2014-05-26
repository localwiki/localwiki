import random

from django.db import connection
from django.views.generic import ListView

from regions.views import RegionMixin
from maps.widgets import InfoMap
from pages.models import Page
from utils.views import MultipleTypesPaginatedView


class BaseExploreList(RegionMixin, MultipleTypesPaginatedView):
    context_object_name = 'pages'
    items_per_page = 100

    def get_object_lists(self):
        qs = Page.objects.filter(region=self.get_region())

        # Exclude meta stuff
        qs = qs.exclude(slug__startswith='templates/')
        qs = qs.exclude(slug='templates')
        qs = qs.exclude(slug='front page')

        return [qs]

    def get_context_data(self, *args, **kwargs):
        context = super(BaseExploreList, self).get_context_data(*args, **kwargs)
        context['map_media'] = InfoMap([]).media
        return context


class RandomExploreList(BaseExploreList):
    def get_template_names(self):
        if self.request.is_ajax():
            return ['explore/page.html']
        return ['explore/random_index.html']

    def get_object_lists(self):
        obj_lists = super(RandomExploreList, self).get_object_lists()
        qs = obj_lists[0]

        # Exclude those with empty scores
        qs = qs.exclude(score=None)

        # We're paginating a random sort, so let's make sure it's
        # deterministic here to avoid duplicate results.
        self.random_seed = float(self.request.GET.get('s', random.random()))
        cursor = connection.cursor()
        cursor.execute("SELECT setseed(%s);" % self.random_seed)

        qs = qs.defer('content').select_related('region').order_by('-score__score', '?')
        return [qs]

    def get_context_data(self, *args, **kwargs):
        context = super(RandomExploreList, self).get_context_data(*args, **kwargs)
        context['page_type'] = 'random'
        context['random_seed'] = self.random_seed
        return context


class AlphabeticalExploreList(BaseExploreList):
    def get_template_names(self):
        if self.request.is_ajax():
            return ['explore/page.html']
        return ['explore/alphabetical_index.html']

    def get_object_lists(self):
        obj_lists = super(AlphabeticalExploreList, self).get_object_lists()
        qs = obj_lists[0]

        qs = qs.defer('content').select_related('region').order_by('name')
        return [qs]

    def get_context_data(self, *args, **kwargs):
        context = super(AlphabeticalExploreList, self).get_context_data(*args, **kwargs)
        context['page_type'] = 'alphabetical'
        return context


class ExploreJustList(RegionMixin, ListView):
    model = Page
    context_object_name = 'pages'
    template_name = 'explore/just_list.html'

    def get_queryset(self):
        qs = super(ExploreJustList, self).get_queryset()

        # Exclude meta stuff
        qs = qs.exclude(slug__startswith='templates/')
        qs = qs.exclude(slug='templates')
        qs = qs.exclude(slug='front page')

        return qs.defer('content').select_related('region')
