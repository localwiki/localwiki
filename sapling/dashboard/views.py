from datetime import datetime, timedelta

from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User
from django.db.models import Max

import pyflot

from pages.models import Page, PageFile
from maps.models import MapData
from redirects.models import Redirect

from versionutils.versioning.constants import *


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard_main.html'

    @method_decorator(cache_page(60 * 60 * 5))
    def get(self, request, *args, **kwargs):
        return super(DashboardView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['num_pages'] = len(Page.objects.all())
        context['num_files'] = len(PageFile.objects.all())
        context['num_maps'] = len(MapData.objects.all())
        context['num_redirects'] = len(Redirect.objects.all())
        context['num_users'] = len(User.objects.all())

        items_over_time = pyflot.Flot()
        edits_over_time = pyflot.Flot()

        now = datetime.now()
        oldest_page = Page.versions.all().order_by(
            'history_date')[0].version_info.date

        num_pages_over_time = []
        num_pages = 0
        num_maps_over_time = []
        num_maps = 0
        num_files_over_time = []
        num_files = 0
        d = datetime(oldest_page.year, oldest_page.month, oldest_page.day)
        while (now.year, now.month, now.day) != (d.year, d.month, d.day):
            next_d = d + timedelta(days=1)
            # Figure out which pages were added, deleted on this day.
            num_added = len(Page.versions.filter(
                version_info__date__gte=d, version_info__date__lt=next_d,
                version_info__type__in=ADDED_TYPES))
            num_deleted = len(Page.versions.filter(
                version_info__date__gte=d, version_info__date__lt=next_d,
                version_info__type__in=DELETED_TYPES))

            num_pages += num_added
            num_pages -= num_deleted
            num_pages_over_time.append((d, num_pages))

            # Figure out which maps were added, deleted on this day.
            num_added = len(MapData.versions.filter(
                version_info__date__gte=d, version_info__date__lt=next_d,
                version_info__type__in=ADDED_TYPES))
            num_deleted = len(MapData.versions.filter(
                version_info__date__gte=d, version_info__date__lt=next_d,
                version_info__type__in=DELETED_TYPES))

            num_maps += num_added
            num_maps -= num_deleted
            num_maps_over_time.append((d, num_maps))

            # Figure out which files were added, deleted on this day.
            num_added = len(PageFile.versions.filter(
                version_info__date__gte=d, version_info__date__lt=next_d,
                version_info__type__in=ADDED_TYPES))
            num_deleted = len(PageFile.versions.filter(
                version_info__date__gte=d, version_info__date__lt=next_d,
                version_info__type__in=DELETED_TYPES))

            num_files += num_added
            num_files -= num_deleted
            num_files_over_time.append((d, num_files))

            d = next_d

        items_over_time.add_time_series(num_pages_over_time, label="pages")
        items_over_time.add_time_series(num_maps_over_time, label="maps")
        items_over_time.add_time_series(num_files_over_time, label="files")
        context['num_items_over_time'] = items_over_time

        # Total item edits over time.
        page_edits = []
        total_page_edits = 0
        map_edits = []
        total_map_edits = 0
        file_edits = []
        total_file_edits = 0
        d = datetime(oldest_page.year, oldest_page.month, oldest_page.day)
        while (now.year, now.month, now.day) != (d.year, d.month, d.day):
            next_d = d + timedelta(days=1)

            # Page edits
            page_edits_this_day = len(Page.versions.filter(
                version_info__date__gte=d, version_info__date__lt=next_d))
            total_page_edits += page_edits_this_day
            page_edits.append((d, total_page_edits))

            # Map edits
            map_edits_this_day = len(MapData.versions.filter(
                version_info__date__gte=d, version_info__date__lt=next_d))
            total_map_edits += map_edits_this_day
            map_edits.append((d, total_map_edits))

            # File edits
            file_edits_this_day = len(PageFile.versions.filter(
                version_info__date__gte=d, version_info__date__lt=next_d))
            total_file_edits += file_edits_this_day
            file_edits.append((d, total_file_edits))

            d = next_d

        edits_over_time.add_time_series(page_edits, label="pages")
        edits_over_time.add_time_series(map_edits, label="maps")
        edits_over_time.add_time_series(file_edits, label="files")
        context['num_edits_over_time'] = edits_over_time

        # Total page contents over time
        page_content_over_time = pyflot.Flot()

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

        page_content_over_time.add_time_series(page_contents)

        context['page_content_over_time'] = page_content_over_time

        return context
