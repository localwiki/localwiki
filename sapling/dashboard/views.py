from datetime import date, datetime, timedelta

from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models import Max
from django.utils.translation import ugettext as _

import pyflot
import qsstats

from pages.models import Page, PageFile
from maps.models import MapData
from redirects.models import Redirect
from utils.views import JSONView

from versionutils.versioning.constants import *

import time

COMPLETE_CACHE_TIME = 60 * 60 * 5
EASIER_CACHE_TIME = 60  # cache easier stuff for 60 seconds.


class DashboardView(JSONView):
    def get_nums(self):
        nums = cache.get('dashboard_nums')
        if nums is None:
            nums = {
                'num_pages': Page.objects.count(),
                'num_files': PageFile.objects.count(),
                'num_maps': MapData.objects.count(),
                'num_redirects': Redirect.objects.count(),
                'num_users': User.objects.count()
            }
            cache.set('dashboard_nums', nums, EASIER_CACHE_TIME)
        return nums

    def get_context_data(self, **kwargs):
        start_at = time.time()   # profiling
        oldest = cache.get('dashboard_oldest')
        if oldest is None:
            qs = Page.versions.order_by('history_date')
            qs = qs.filter(history_date__gte=date(2000, 1, 1))
            oldest = qs[0].version_info.date
            cache.set('dashboard_oldest', oldest, COMPLETE_CACHE_TIME)
        context = cache.get('dashboard')
        if context is not None:
            context.update(self.get_nums())
            return context

        if 'check_cache' in self.request.GET:
            # We tell the browser it hasn't been generated yet, and the browser
            # then shows a "loading" message as the page is generated.
            # TODO: Make this process better.  Job-queue + structured
            # poll/socketio.
            context = {'generated': False}
        else:
            if cache.get('dashboard_generating'):
                # Cache is generating in a different request.
                return {'generated': False}

            cache.set('dashboard_generating', True)
            context = {
                'num_items_over_time': items_over_time(oldest),
                '_duration_items': time.time() - start_at,
                'num_edits_over_time': edits_over_time(oldest),
                '_duration_edits': time.time() - start_at,
                'page_content_over_time': page_content_over_time(oldest),
                '_duration_pagecontent': time.time() - start_at,
                'users_registered_over_time': users_registered_over_time(),
                '_duration_urot': time.time() - start_at,
            }
            context.update(self.get_nums())
            context['_duration_getnums'] = time.time() - start_at

            context['generated'] = True
            # This is either too huge to cache, or small enough that we don't
            # need to cache.  Only way to win is not to play at all.
            #cache.set('dashboard', context, COMPLETE_CACHE_TIME)
            cache.set('dashboard_generating', False)

        return context


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


def items_over_time(oldest_page):
    graph = pyflot.Flot()

    pages_added = qsstats.QuerySetStats(
        Page.versions.filter(version_info__type__in=ADDED_TYPES),
        'history_date').time_series(oldest_page)
    pages_deleted = qsstats.QuerySetStats(
        Page.versions.filter(version_info__type__in=DELETED_TYPES),
        'history_date').time_series(oldest_page)
    num_pages_over_time = _sum_from_add_del(pages_added, pages_deleted)

    maps_added = qsstats.QuerySetStats(
        MapData.versions.filter(version_info__type__in=ADDED_TYPES),
        'history_date').time_series(oldest_page)
    maps_deleted = qsstats.QuerySetStats(
        MapData.versions.filter(version_info__type__in=DELETED_TYPES),
        'history_date').time_series(oldest_page)
    num_maps_over_time = _sum_from_add_del(maps_added, maps_deleted)

    files_added = qsstats.QuerySetStats(
        PageFile.versions.filter(version_info__type__in=ADDED_TYPES),
        'history_date').time_series(oldest_page)
    files_deleted = qsstats.QuerySetStats(
        PageFile.versions.filter(version_info__type__in=DELETED_TYPES),
        'history_date').time_series(oldest_page)
    num_files_over_time = _sum_from_add_del(files_added, files_deleted)

    redir_added = qsstats.QuerySetStats(
        Redirect.versions.filter(version_info__type__in=ADDED_TYPES),
        'history_date').time_series(oldest_page)
    redir_deleted = qsstats.QuerySetStats(
        Redirect.versions.filter(version_info__type__in=DELETED_TYPES),
        'history_date').time_series(oldest_page)
    num_redirects_over_time = _sum_from_add_del(redir_added, redir_deleted)

    graph.add_time_series(num_pages_over_time, label=_("pages"))
    graph.add_time_series(num_maps_over_time, label=_("maps"))
    graph.add_time_series(num_files_over_time, label=_("files"))
    graph.add_time_series(num_redirects_over_time,
        label=_("redirects"))

    return [graph.prepare_series(s) for s in graph._series]


def edits_over_time(oldest_page):
    graph = pyflot.Flot()

    qss = qsstats.QuerySetStats(Page.versions.all(), 'history_date')
    graph.add_time_series(qss.time_series(oldest_page), label=_("pages"))

    qss = qsstats.QuerySetStats(MapData.versions.all(), 'history_date')
    graph.add_time_series(qss.time_series(oldest_page), label=_("maps"))

    qss = qsstats.QuerySetStats(PageFile.versions.all(), 'history_date')
    graph.add_time_series(qss.time_series(oldest_page), label=_("files"))

    qss = qsstats.QuerySetStats(Redirect.versions.all(), 'history_date')
    graph.add_time_series(qss.time_series(oldest_page), label=_("redirects"))

    return [graph.prepare_series(s) for s in graph._series]


def page_content_over_time(oldest_page):
    qs = Page.versions.extra({'content_length': "length(content)",
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

    graph.add_time_series(page_contents)
    return [graph.prepare_series(s) for s in graph._series]


def users_registered_over_time():
    oldest_user = User.objects.order_by('date_joined')[0].date_joined
    graph = pyflot.Flot()

    qss = qsstats.QuerySetStats(User.objects.all(), 'date_joined')
    graph.add_time_series(_summed_series(qss.time_series(oldest_user)))

    return [graph.prepare_series(s) for s in graph._series]
