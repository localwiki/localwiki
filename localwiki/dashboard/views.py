from datetime import date, datetime, timedelta

from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models import Max
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.contrib.humanize.templatetags.humanize import intcomma

import pyflot
import qsstats

from pages.models import Page, PageFile
from regions.models import Region
from maps.models import MapData
from redirects.models import Redirect
from utils.views import JSONView

from versionutils.versioning.constants import *

import time

COMPLETE_CACHE_TIME = 60 * 60 * 5
EASIER_CACHE_TIME = 60  # cache easier stuff for 60 seconds.


class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super(TemplateView, self).get_context_data(*args, **kwargs)
        if self.kwargs.get('region'):
            context['region'] = Region.objects.get(slug=self.kwargs.get('region'))
        return context


def humanize(i):
    return intcomma(i)


class DashboardRenderView(JSONView):
    def get_filters(self):
        if self.kwargs.get('region'):
            return {'region': Region.objects.get(slug=self.kwargs.get('region'))}
        return {}

    def cache_prefix(self):
        if self.kwargs.get('region'):
            return 'region:%s' % self.kwargs.get('region')
        return ''

    def get_nums(self):
        filters = self.get_filters()
        prefix = self.cache_prefix()
        nums = cache.get('%s:dashboard_nums' % prefix)
        if nums is None:
            nums = {
                'num_pages': humanize(Page.objects.filter(**filters).count()),
                'num_files': humanize(PageFile.objects.filter(**filters).count()),
                'num_maps': humanize(MapData.objects.filter(**filters).count()),
                'num_redirects': humanize(Redirect.objects.filter(**filters).count()),
                'num_users': humanize(User.objects.count())
            }
            cache.set('%s:dashboard_nums' % prefix, nums,
                EASIER_CACHE_TIME)
            nums['_regenerated_nums'] = True
        nums['generated'] = True
        return nums

    def get_oldest_page_date(self):
        filters = self.get_filters()
        prefix = self.cache_prefix()
        oldest = cache.get('%s:dashboard_oldest' % prefix)
        if oldest is None:
            qs = Page.versions.filter(**filters).order_by('history_date')
            qs = qs.filter(history_date__gte=date(2000, 1, 1))
            if not qs.exists():
                return None
            oldest = qs[0].version_info.date
            cache.set('%s:dashboard_oldest' % prefix, oldest, COMPLETE_CACHE_TIME)
        return oldest

    def get_context_data_for_chart(self, function, key):
        filters = self.get_filters()
        prefix = self.cache_prefix()
        context = cache.get('%s:dashboard_%s' % (prefix, key))

        if context is not None:
            context['_cached'] = True
            context['_age'] = time.time() - context['_built']
            context['generated'] = True
            return context

        start_at = time.time()
        oldest = self.get_oldest_page_date()

        if oldest is None:
            # We probably have no pages yet
            return {'generated': True, key: [], '_error': 'No page data'}

        if 'check_cache' in self.request.GET or cache.get('%s:dashboard_generating_%s' % (prefix, key), False):
            return {'generated': False}

        cache.set('%s:dashboard_generating_%s' % (prefix, key), True, 60)

        context = {}
        context[key] = function(oldest, filters)

        context['_built'] = time.time()
        context['_duration'] = time.time() - start_at
        context['generated'] = True
        cache.set('%s:dashboard_%s' % (prefix, key), context, COMPLETE_CACHE_TIME)
        cache.set('%s:dashboard_generating_%s' % (prefix, key), False)

        context['_age'] = time.time() - context['_built']
        context['_cached'] = False

        return context

    def get_context_data(self, *args, **kwargs):
        if 'graph' in self.request.GET:
            if self.request.GET.get('graph', None) == 'num_items_over_time':
                return self.get_context_data_for_chart(items_over_time, 'num_items_over_time')
            elif self.request.GET.get('graph', None) == 'num_edits_over_time':
                return self.get_context_data_for_chart(edits_over_time, 'num_edits_over_time')
            elif self.request.GET.get('graph', None) == 'users_registered_over_time':
                return self.get_context_data_for_chart(users_registered_over_time, 'users_registered_over_time')
            elif self.request.GET.get('graph', None) == 'page_content_over_time':
                return self.get_context_data_for_chart(page_content_over_time, 'page_content_over_time')

        return self.get_nums()


def _summed_series(series):
    """
    Take a time series, ``series``, and turn it into a summed-by-term series.
    """
    sum = 0
    l = []
    for (d, num) in series:
        sum += num
        l.append((d, sum))
    return l


def _sum_from_add_del(added_series, deleted_series):
    """
    Sum the provided, aligned time series (added, deleted).
    """
    sum = 0
    l = []
    for ((d, added), (_, deleted)) in zip(added_series, deleted_series):
        sum += (added - deleted)
        l.append((d, sum))
    return l


def items_over_time(oldest_page, filters):
    graph = pyflot.Flot()

    pages_added = qsstats.QuerySetStats(
        Page.versions.filter(version_info__type__in=ADDED_TYPES, **filters),
        'history_date').time_series(oldest_page)
    pages_deleted = qsstats.QuerySetStats(
        Page.versions.filter(version_info__type__in=DELETED_TYPES, **filters),
        'history_date').time_series(oldest_page)
    num_pages_over_time = _sum_from_add_del(pages_added, pages_deleted)

    maps_added = qsstats.QuerySetStats(
        MapData.versions.filter(version_info__type__in=ADDED_TYPES, **filters),
        'history_date').time_series(oldest_page)
    maps_deleted = qsstats.QuerySetStats(
        MapData.versions.filter(version_info__type__in=DELETED_TYPES, **filters),
        'history_date').time_series(oldest_page)
    num_maps_over_time = _sum_from_add_del(maps_added, maps_deleted)

    files_added = qsstats.QuerySetStats(
        PageFile.versions.filter(version_info__type__in=ADDED_TYPES, **filters),
        'history_date').time_series(oldest_page)
    files_deleted = qsstats.QuerySetStats(
        PageFile.versions.filter(version_info__type__in=DELETED_TYPES, **filters),
        'history_date').time_series(oldest_page)
    num_files_over_time = _sum_from_add_del(files_added, files_deleted)

    redir_added = qsstats.QuerySetStats(
        Redirect.versions.filter(version_info__type__in=ADDED_TYPES, **filters),
        'history_date').time_series(oldest_page)
    redir_deleted = qsstats.QuerySetStats(
        Redirect.versions.filter(version_info__type__in=DELETED_TYPES, **filters),
        'history_date').time_series(oldest_page)
    num_redirects_over_time = _sum_from_add_del(redir_added, redir_deleted)

    graph.add_time_series(num_pages_over_time, label=_("pages"))
    graph.add_time_series(num_maps_over_time, label=_("maps"))
    graph.add_time_series(num_files_over_time, label=_("files"))
    graph.add_time_series(num_redirects_over_time,
        label=_("redirects"))

    return [graph.prepare_series(s) for s in graph._series]


def edits_over_time(oldest_page, filters):
    graph = pyflot.Flot()

    qss = qsstats.QuerySetStats(Page.versions.filter(**filters), 'history_date')
    graph.add_time_series(qss.time_series(oldest_page), label=_("pages"))

    qss = qsstats.QuerySetStats(MapData.versions.filter(**filters), 'history_date')
    graph.add_time_series(qss.time_series(oldest_page), label=_("maps"))

    qss = qsstats.QuerySetStats(PageFile.versions.filter(**filters), 'history_date')
    graph.add_time_series(qss.time_series(oldest_page), label=_("files"))

    qss = qsstats.QuerySetStats(Redirect.versions.filter(**filters), 'history_date')
    graph.add_time_series(qss.time_series(oldest_page), label=_("redirects"))

    return [graph.prepare_series(s) for s in graph._series]


def page_content_over_time(oldest_page, filters):
    qs = Page.versions.filter(**filters).extra(
        {'content_length': "length(content)",
         'history_day': "date(history_date)"})
    qs = qs.order_by('history_day')
    qs = qs.values('content_length', 'history_day', 'slug')

    graph = pyflot.Flot()
    page_dict = {}
    page_contents = []
    current_day = oldest_page.date()

    for page in qs.iterator():
        if page['history_day'] > current_day:
            page_contents.append((current_day, sum(page_dict.values())))
            current_day = page['history_day']
        page_dict[page['slug']] = page['content_length']

    if page_contents:
        graph.add_time_series(page_contents)
        return [graph.prepare_series(s) for s in graph._series]
    return []


def users_registered_over_time(oldest_page, filters):
    oldest_user = User.objects.order_by('date_joined')[0].date_joined
    graph = pyflot.Flot()

    qss = qsstats.QuerySetStats(User.objects.all(), 'date_joined')
    graph.add_time_series(_summed_series(qss.time_series(oldest_user)))

    return [graph.prepare_series(s) for s in graph._series]
