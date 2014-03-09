import datetime
from itertools import groupby
from collections import defaultdict

from django.http import Http404
from django.core.urlresolvers import reverse

from versionutils.versioning.constants import *
from regions.views import RegionMixin
from localwiki.utils.views import MultipleTypesPaginatedView

from . import get_changes_classes

IGNORE_TYPES = [
    TYPE_DELETED_CASCADE,
    TYPE_REVERTED_DELETED_CASCADE,
    TYPE_REVERTED_CASCADE
]


class RecentChangesView(RegionMixin, MultipleTypesPaginatedView):
    template_name = "recentchanges/recentchanges.html"
    context_object_name = 'changes'

    def get_template_names(self):
        if self.request.is_ajax():
            return ['recentchanges/index_page.html']
        return ['recentchanges/index.html']

    def get_object_lists(self):
        change_sets = []
        region = self.get_region()

        for change_class in get_changes_classes():
            change_obj = change_class(region=region)
            change_set = change_obj.queryset().filter(region=region)
            change_sets.append(change_set)

        return change_sets

    def get_pagination_merge_key(self):
        """
        Returns:
            A callable that, when called, returns the value to use for the merge +
            sort.  Default: the value inside the list itself.
        """
        return (lambda x: x.version_info.date)

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
