from datetime import datetime, timedelta

from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models import Max

import pyflot

from pages.models import Page, PageFile
from maps.models import MapData
from redirects.models import Redirect
from utils.views import JSONView

from versionutils.versioning.constants import *

COMPLETE_CACHE_TIME = 60 * 60 * 5
EASIER_CACHE_TIME = 60  # cache easier stuff for 60 seconds.


class DashboardView(JSONView):
    def get_nums(self):
        nums = cache.get('dashboard_nums')
        if nums is None:
            nums = {
                'num_pages': len(Page.objects.all()),
                'num_files': len(PageFile.objects.all()),
                'num_maps': len(MapData.objects.all()),
                'num_redirects': len(Redirect.objects.all()),
                'num_users': len(User.objects.all())
            }
            cache.set('dashboard_nums', nums, EASIER_CACHE_TIME)
        return nums

    def get_context_data(self, **kwargs):
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
            now = datetime.now()
            context = {
                'num_items_over_time': items_over_time(now),
                'num_edits_over_time': edits_over_time(now),
                'page_content_over_time': page_content_over_time(now),
                'users_registered_over_time': users_registered_over_time(now),
            }
            context.update(self.get_nums())

            context['generated'] = True
            cache.set('dashboard', context, CACHE_TIME)
            cache.set('dashboard_generating', False)

        return context


def items_over_time(now):
    def _total_count_as_of(d, M, total_count):
        # Figure out which instances of M were added, deleted on this day.
        num_added = len(M.versions.filter(
            version_info__date__gte=d, version_info__date__lt=next_d,
            version_info__type__in=ADDED_TYPES))
        num_deleted = len(M.versions.filter(
            version_info__date__gte=d, version_info__date__lt=next_d,
            version_info__type__in=DELETED_TYPES))

        total_count += num_added
        total_count -= num_deleted
        return total_count

    oldest_page = Page.versions.all().order_by(
        'history_date')[0].version_info.date

    graph = pyflot.Flot()
    page_total_count, map_total_count, file_total_count, \
        redirect_total_count = 0, 0, 0, 0
    num_pages_over_time, num_maps_over_time, num_files_over_time, \
        num_redirects_over_time = [], [], [], []
    # Start at the oldest page's date and then iterate, day-by-day, until
    # current day, day by day.
    d = datetime(oldest_page.year, oldest_page.month, oldest_page.day)
    while (now.year, now.month, now.day) != (d.year, d.month, d.day):
        next_d = d + timedelta(days=1)

        page_total_count = _total_count_as_of(d, Page, page_total_count)
        num_pages_over_time.append((d, page_total_count))

        map_total_count = _total_count_as_of(d, MapData, map_total_count)
        num_maps_over_time.append((d, map_total_count))

        file_total_count = _total_count_as_of(d, PageFile,
            file_total_count)
        num_files_over_time.append((d, file_total_count))

        redirect_total_count = _total_count_as_of(d, Redirect,
            redirect_total_count)
        num_redirects_over_time.append((d, redirect_total_count))

        d = next_d

    graph.add_time_series(num_pages_over_time, label="pages")
    graph.add_time_series(num_maps_over_time, label="maps")
    graph.add_time_series(num_files_over_time, label="files")
    graph.add_time_series(num_redirects_over_time,
        label="redirects")

    return [graph.prepare_series(s) for s in graph._series]


def edits_over_time(now):
    oldest_page = Page.versions.all().order_by(
        'history_date')[0].version_info.date

    graph = pyflot.Flot()
    page_edits = []
    map_edits = []
    file_edits = []
    redirect_edits = []
    d = datetime(oldest_page.year, oldest_page.month, oldest_page.day)
    while (now.year, now.month, now.day) != (d.year, d.month, d.day):
        next_d = d + timedelta(days=1)

        # Page edits
        page_edits_this_day = len(Page.versions.filter(
            version_info__date__gte=d, version_info__date__lt=next_d))
        page_edits.append((d, page_edits_this_day))

        # Map edits
        map_edits_this_day = len(MapData.versions.filter(
            version_info__date__gte=d, version_info__date__lt=next_d))
        map_edits.append((d, map_edits_this_day))

        # File edits
        file_edits_this_day = len(PageFile.versions.filter(
            version_info__date__gte=d, version_info__date__lt=next_d))
        file_edits.append((d, file_edits_this_day))

        # Redirect edits
        redirect_edits_this_day = len(Redirect.versions.filter(
            version_info__date__gte=d, version_info__date__lt=next_d))
        redirect_edits.append((d, redirect_edits_this_day))

        d = next_d

    graph.add_time_series(page_edits, label="pages")
    graph.add_time_series(map_edits, label="maps")
    graph.add_time_series(file_edits, label="files")
    graph.add_time_series(redirect_edits, label="redirects")

    return [graph.prepare_series(s) for s in graph._series]


def page_content_over_time(now):
    oldest_page = Page.versions.all().order_by(
        'history_date')[0].version_info.date

    graph = pyflot.Flot()
    page_dict = {}
    page_contents = []

    d = datetime(oldest_page.year, oldest_page.month, oldest_page.day)
    while (now.year, now.month, now.day) != (d.year, d.month, d.day):
        next_d = d + timedelta(days=1)

        page_edits_this_day = Page.versions.filter(
            version_info__date__gte=d, version_info__date__lt=next_d)
        # Group the edits by slug and annotate with the max history date
        # for the associated page.
        slugs_with_date = page_edits_this_day.values('slug').annotate(
            Max('history_date')).order_by()

        for item in slugs_with_date:
            p = Page(slug=item['slug'])
            # Grab the historical version at this date.
            p_h = p.versions.as_of(date=item['history_date__max'])
            page_dict[item['slug']] = len(p_h.content)

        total_content_today = 0
        for slug, length in page_dict.iteritems():
            total_content_today += length

        page_contents.append((d, total_content_today))
        d = next_d

    graph.add_time_series(page_contents)

    return [graph.prepare_series(s) for s in graph._series]


def users_registered_over_time(now):
    oldest_user = User.objects.order_by('date_joined')[0].date_joined

    graph = pyflot.Flot()
    users_registered = []
    num_users = 0
    d = datetime(oldest_user.year, oldest_user.month, oldest_user.day)
    while (now.year, now.month, now.day) != (d.year, d.month, d.day):
        next_d = d + timedelta(days=1)

        users_this_day = len(User.objects.filter(
            date_joined__gte=d, date_joined__lt=next_d))

        num_users += users_this_day

        users_registered.append((d, num_users))
        d = next_d

    graph.add_time_series(users_registered)

    return [graph.prepare_series(s) for s in graph._series]
