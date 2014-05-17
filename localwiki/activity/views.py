import datetime
from itertools import groupby
from collections import defaultdict

from django.http import Http404
from django.core.urlresolvers import reverse

from follow.models import Follow
from actstream.models import actor_stream, Action

from versionutils.versioning.constants import *
from regions.views import RegionMixin
from localwiki.utils.views import MultipleTypesPaginatedView

from . import get_changes_classes

IGNORE_TYPES = [
    TYPE_DELETED_CASCADE,
    TYPE_REVERTED_DELETED_CASCADE,
    TYPE_REVERTED_CASCADE
]


class RegionActivity(RegionMixin, MultipleTypesPaginatedView):
    context_object_name = 'changes'

    def get_template_names(self):
        if self.request.is_ajax():
            return ['activity/index_page.html']
        return ['activity/index.html']

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
        c = super(RegionActivity, self).get_context_data(*args, **kwargs)
        c.update({
            'rc_url': reverse('region-activity',
                kwargs={'region': self.get_region().slug}),
            'ignore_types': IGNORE_TYPES,
            'added_types': ADDED_TYPES,
            'deleted_types': DELETED_TYPES,
            'reverted_types': REVERTED_TYPES,
        })
        return c


class FollowedActivity(MultipleTypesPaginatedView):
    context_object_name = 'changes'

    def get_template_names(self):
        if self.request.is_ajax():
            return ['activity/followed_activity_page.html']
        return ['activity/followed_activity_index.html']

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
            change_set = change_obj.queryset().none()

            ###############################################
            # First, let's get the followed pages' changes
            ###############################################
            attr = change_obj.get_page_lookup_info()
            key = "%s__in" % attr

            for region, pages_followed_slugs in followed_by_region.iteritems():
                change_obj.region = region
                lookups = {
                    'region': region,
                    key: pages_followed_slugs,
                }
                # We use the queryset OR here so we avoid multiple queries.
                change_set = change_set | change_obj.queryset().filter(**lookups)

            ###############################################
            # Now let's get the followed region's changes
            ###############################################
            regions_followed = Follow.objects.filter(user=self.request.user).\
                exclude(target_region=None).\
                select_related('target_region')

            for follow in regions_followed:
                change_obj.region = follow.target_region
                change_set = change_set | change_obj.queryset().filter(region=follow.target_region)

            change_sets.append(change_set)

        ###############################################
        # The action (actstream) for users we follow
        ###############################################
        action_set = Action.objects.none()
        for follow in Follow.objects.filter(user=self.request.user).\
            exclude(target_user=None).\
            exclude(target_user=self.request.user).\
            select_related('target_user'):

            action_set = action_set | actor_stream(follow.target_user)
        change_sets.append(action_set)

        return change_sets

    def get_pagination_merge_key(self):
        """
        Returns:
            A callable that, when called, returns the value to use for the merge +
            sort.  Default: the value inside the list itself.
        """
        def _f(x):
            if isinstance(x, Action):
                return x.timestamp
            return x.version_info.date
        return (_f)

    def get_context_data(self, *args, **kwargs):
        c = super(FollowedActivity, self).get_context_data(*args, **kwargs)
        c.update({
            'ignore_types': IGNORE_TYPES,
            'added_types': ADDED_TYPES,
            'deleted_types': DELETED_TYPES,
            'reverted_types': REVERTED_TYPES,
        })
        return c
