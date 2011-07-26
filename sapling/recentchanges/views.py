import datetime

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
    context_object_name = 'changes_grouped_by_slug'

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

        return self._group_by_date_then_slug(objs)

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

    def _group_by_date_then_slug(self, objs):
        """
        Returns a list of the form [ (first_change, [change1, change2, ...]) ].
        The list is grouped by the slug.
        """
        slug_dict = {}
        # objs is currently ordered by date.  Group together by slug.
        for obj in objs:
            # For use in the template.
            if not hasattr(obj, 'diff_view'):
                obj.diff_view = '%s:compare-dates' % obj._meta.app_label

            changes_for_slug = slug_dict.get(obj.slug, [])
            changes_for_slug.append(obj)
            slug_dict[obj.slug] = changes_for_slug

        # Sort the grouped slugs by the first date in the slug's change
        # list.
        objs_by_slug = sorted(slug_dict.values(),
               key=lambda x: x[0].history_info.date, reverse=True)

        l = []
        for items in objs_by_slug:
            l.append((items[0], items))
        return l

    def _get_start_date(self):
        days_back = int(self.request.GET.get('days_back', '2'))
        if days_back > MAX_DAYS_BACK:
            raise Http404("Days must be less than %s" % MAX_DAYS_BACK)

        # If days_back is N we will (try and) show N days worth of changes,
        # not simply the latest N days' changes.  We always want to show as
        # many changes on the RC page as possible to encourage more wiki
        # activity.
        try:
            latest_changes = Page.history.all()[0:300]
            start_at = Page.history.all()[0].history_info.date
            num_days_total = 1

            for change in latest_changes:
                if change.history_info.date.day != start_at.day:
                    start_at = change.history_info.date
                    num_days_total += 1
                if num_days_total == days_back:
                    break
        except IndexError:
            start_at = datetime.datetime.now()

        days_back = datetime.timedelta(days=num_days_total)

        # Set to the beginning of that day.
        return datetime.datetime(start_at.year, start_at.month, start_at.day,
            0, 0, 0, 0, start_at.tzinfo)
