import datetime
from itertools import groupby

from django.views.generic import ListView
from django.http import Http404
from django.core.urlresolvers import reverse

from versionutils.versioning.constants import *
from pages.models import Page

from utils import merge_changes
from recentchanges import get_changes_classes

MAX_DAYS_BACK = 7
IGNORE_TYPES = [
    TYPE_DELETED_CASCADE,
    TYPE_REVERTED_DELETED_CASCADE,
    TYPE_REVERTED_CASCADE
]


class RecentChangesView(ListView):
    template_name = "recentchanges/recentchanges.html"
    context_object_name = 'changes_grouped_by_day'

    def format_change_set(self, change_obj, change_set):
        for obj in change_set:
            obj.classname = change_obj.classname
            obj.page = change_obj.page(obj)
            obj.slug = obj.page.slug
            obj.diff_url = change_obj.diff_url(obj)
        return change_set

    def get_queryset(self):
        change_sets = []
        start_at = self._get_start_date()

        for change_class in get_changes_classes():
            change_obj = change_class()
            change_set = change_obj.queryset(start_at)
            change_sets.append(
                self.format_change_set(change_obj, change_set))

        # Merge the sorted-by-date querysets.
        objs = merge_changes(change_sets)

        return self._changes_grouped_by_day(objs)

    def get_context_data(self, *args, **kwargs):
        c = super(RecentChangesView, self).get_context_data(*args, **kwargs)
        c.update({
            'rc_url': reverse('recentchanges'),
            'ignore_types': IGNORE_TYPES,
            'added_types': ADDED_TYPES,
            'deleted_types': DELETED_TYPES,
            'reverted_types': REVERTED_TYPES,
        })
        return c

    def _changes_grouped_by_day(self, objs):
        """
        Args:
            objs: A grouped-by-day list of changes.

        Returns:
            A list of the form:
            [
              {'day': datetime representing the day,
               'changes': a slug-grouped list of changes
              },
              ...
            ]

            the slug-grouped list of changes is of the form:
            [ changes, changes, ...]

            where 'changes' are each a list of changes associated
            with a given slug.  The list-of-changes-lists is ordered
            by the most recent edit in each 'changes' list.
        """
        def _the_day(o):
            date = o.version_info.date
            return (date.year, date.month, date.day)

        l = []
        # Group objs by day.
        for day, changes in groupby(objs, _the_day):
            slug_dict = {}
            # For each day, group changes by slug.
            for change in changes:
                changes_for_slug = slug_dict.get(change.slug, [])
                changes_for_slug.append(change)
                slug_dict[change.slug] = changes_for_slug

            # Sort the slug_dict by the most recent edit date of each
            # slug's set of changes.
            by_most_recent_edit = sorted(slug_dict.values(),
                key=lambda x: x[0].version_info.date, reverse=True)

            # Without loss of generality, grab a datetime object
            # representing the day.
            the_day = slug_dict.values()[0][0].version_info.date

            l.append({'day': the_day, 'changes': by_most_recent_edit})

        return l

    def _get_start_date(self):
        days_back = int(self.request.GET.get('days_back', '2'))
        if days_back > MAX_DAYS_BACK:
            raise Http404("Days must be less than %s" % MAX_DAYS_BACK)

        # If days_back is N we will (try and) show N days worth of changes,
        # not simply the latest N days' changes.  We always want to show as
        # many changes on the RC page as possible to encourage more wiki
        # activity.
        num_days_total = 1
        try:
            latest_changes = Page.versions.all()[0:300]
            start_at = Page.versions.all()[0].version_info.date

            for change in latest_changes:
                if change.version_info.date.day != start_at.day:
                    start_at = change.version_info.date
                    num_days_total += 1
                if num_days_total == days_back:
                    break
        except IndexError:
            start_at = datetime.datetime.now()

        days_back = datetime.timedelta(days=num_days_total)

        # Set to the beginning of that day.
        return datetime.datetime(start_at.year, start_at.month, start_at.day,
            0, 0, 0, 0, start_at.tzinfo)
