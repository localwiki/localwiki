import datetime
from itertools import groupby
from collections import defaultdict

from django.http import Http404
from django.core.urlresolvers import reverse

from follow.models import Follow

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


class FollowedActivityFeed(MultipleTypesPaginatedView):
    context_object_name = 'changes'

    def get_template_names(self):
        if self.request.is_ajax():
            return ['recentchanges/followed_activity_page.html']
        return ['recentchanges/followed_activity_index.html']

    def get_object_lists(self):
        change_sets = []

        pages_followed = Follow.objects.filter(user=self.request.user).\
            exclude(target_page=None).\
            select_related('target_page').\
            only('target_page__slug', 'target_page__region__id')

        # XXX Possibily inefficient to iterate through
        # all the regions-they-have-a-page-they-follow-in
        # here, but alternatives seem too complex to write right
        # now.
        followed_by_region = defaultdict(list)
        for f in pages_followed:
            slug, region_id = f.target_page.slug, f.target_page.region_id
            followed_by_region[region_id].append(slug)

        for change_class in get_changes_classes():
            change_obj = change_class()

            attr = change_obj.get_page_lookup_info()
            key = "%s__in" % attr

            change_set = change_obj.queryset().none()
            for region, pages_followed_slugs in followed_by_region.iteritems():
                change_obj.region = region
                lookups = {
                    'region': region,
                    key: pages_followed_slugs,
                }
                change_set = change_set | change_obj.queryset().filter(**lookups)

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
        c = super(FollowedActivityFeed, self).get_context_data(*args, **kwargs)
        c.update({
            'ignore_types': IGNORE_TYPES,
            'added_types': ADDED_TYPES,
            'deleted_types': DELETED_TYPES,
            'reverted_types': REVERTED_TYPES,
        })
        return c
