import datetime
from itertools import groupby

from django.views.generic import ListView
from django.http import Http404
from django.core.urlresolvers import reverse

from versionutils.versioning.constants import *
from pages.models import Page
from regions.views import RegionMixin

from utils import merge_changes
from recentchanges import get_changes_classes

MAX_CHANGES = 500
IGNORE_TYPES = [
    TYPE_DELETED_CASCADE,
    TYPE_REVERTED_DELETED_CASCADE,
    TYPE_REVERTED_CASCADE
]


class RecentChangesView(RegionMixin, ListView):
    template_name = "recentchanges/recentchanges.html"
    context_object_name = 'changes'

    def get_template_names(self):
        if self.request.is_ajax():
            return ['recentchanges/index_page.html']
        return ['recentchanges/index.html']

    def format_change_set(self, change_obj, change_set):
        for obj in change_set:
            obj.classname = change_obj.classname
            obj.page = change_obj.page(obj)
            obj.slug = obj.page.slug
            obj.diff_url = change_obj.diff_url(obj)
        return change_set

    def get_queryset(self):
        change_sets = []
        region = self.get_region()

        for change_class in get_changes_classes():
            change_obj = change_class(region=region)
            change_set = change_obj.queryset()
            change_sets.append(
                self.format_change_set(change_obj, change_set))

        # Merge the sorted-by-date querysets.
        objs = merge_changes(change_sets)

        return self._changes_grouped_by_slug(objs)

    def get_context_data(self, *args, **kwargs):
        c = super(RecentChangesView, self).get_context_data(*args, **kwargs)
        c.update({
            'rc_url': reverse('recentchanges',
                kwargs={'region': self.get_region().slug}),
            'ignore_types': IGNORE_TYPES,
            'added_types': ADDED_TYPES,
            'deleted_types': DELETED_TYPES,
            'reverted_types': REVERTED_TYPES,
        })
        return c

    def _changes_grouped_by_slug(self, objs):
        """
        Returns:
            A list of the form:
            [
               [ changes, changes, ... ],
               [ changes, changes, ... ],
               ...
            ]

            where each group of [ changes, ..] is grouped by slug.
            The list is ordered by the most recent edit in each
            [changes, ..] list.
        """
        slug_dict = {}
        # group changes by slug.
        for change in objs:
            changes_for_slug = slug_dict.get(change.slug, [])
            changes_for_slug.append(change)
            slug_dict[change.slug] = changes_for_slug

        # Sort the slug_dict by the most recent edit date of each
        # slug's set of changes.
        by_most_recent_edit = sorted(slug_dict.values(),
            key=lambda x: x[0].version_info.date, reverse=True)

        return by_most_recent_edit
