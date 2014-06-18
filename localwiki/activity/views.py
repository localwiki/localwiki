import datetime
from itertools import groupby
from collections import defaultdict

from django.http import Http404
from django.contrib.auth.models import User

from follow.models import Follow

from versionutils.versioning.constants import *
from regions.views import RegionMixin
from localwiki.utils.urlresolvers import reverse
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
        from actstream.models import actor_stream, Action
        from pages.models import Page, slugify

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

        # Special case: own user pages
        # TODO: use users.views.get_user_page() here once we unify user pages
        change_sets.append(Page.versions.filter(slug=slugify('users/%s' % self.request.user.username)))

        return change_sets

    def get_pagination_merge_key(self):
        """
        Returns:
            A callable that, when called, returns the value to use for the merge +
            sort.  Default: the value inside the list itself.
        """
        from actstream.models import Action
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


class UserActivity(MultipleTypesPaginatedView):
    context_object_name = 'changes'

    def get_template_names(self):
        if self.request.is_ajax():
            return ['activity/followed_activity_page.html']
        return ['activity/user_activity_index.html']

    def get_object_lists(self):
        change_sets = []
        username = self.kwargs.get('username')
        obj_type = self.request.GET.get('type', None)

        for change_class in get_changes_classes():
            # Allow the change_class to be specified via the
            # 'type' query argument
            if obj_type:
                if change_class.classname != obj_type:
                    continue
            change_obj = change_class()
            change_set = change_obj.queryset().filter(version_info__user__username=username)
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
        c = super(UserActivity, self).get_context_data(*args, **kwargs)
        c.update({
            'user_for_page': User.objects.get(username=self.kwargs.get('username')),
            'ignore_types': IGNORE_TYPES,
            'added_types': ADDED_TYPES,
            'deleted_types': DELETED_TYPES,
            'reverted_types': REVERTED_TYPES,
        })
        return c


class AllActivity(MultipleTypesPaginatedView):
    context_object_name = 'changes'

    def get_template_names(self):
        if self.request.is_ajax():
            return ['activity/followed_activity_page.html']
        return ['activity/all_activity_index.html']

    def get_object_lists(self):
        from actstream.models import Action

        change_sets = []

        for change_class in get_changes_classes():
            change_obj = change_class()
            change_set = change_obj.queryset()
            change_sets.append(change_set)

        ####################################################
        # The action (actstream) for all users, if selected
        ####################################################
        #if self.request.GET.get('user_activity', None):
        action_set = Action.objects.exclude(verb='created page')
        # Remove redundant actions that are already shown in the
        # historical lists (e.g. "Philip created a new page")
        change_sets.append(action_set)

        return change_sets

    def get_pagination_merge_key(self):
        """
        Returns:
            A callable that, when called, returns the value to use for the merge +
            sort.  Default: the value inside the list itself.
        """
        from actstream.models import Action

        def _f(x):
            if isinstance(x, Action):
                return x.timestamp
            return x.version_info.date
        return (_f)

    def get_context_data(self, *args, **kwargs):
        c = super(AllActivity, self).get_context_data(*args, **kwargs)
        c.update({
            'ignore_types': IGNORE_TYPES,
            'added_types': ADDED_TYPES,
            'deleted_types': DELETED_TYPES,
            'reverted_types': REVERTED_TYPES,
        })
        return c

