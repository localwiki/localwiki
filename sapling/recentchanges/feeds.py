from django.contrib.syndication.views import Feed
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse

from versionutils.versioning.constants import *

from utils import merge_changes
from views import IGNORE_TYPES
from recentchanges import get_changes_classes

MAX_CHANGES = 500


class RecentChangesFeed(Feed):
    """
    Recent Changes feed for the whole site.
    """
    def site(self):
        if not hasattr(self, '_current_site'):
            self._current_site = get_current_site(self.request)
        return self._current_site

    def title(self):
        return "Recent Changes on %s" % self.site().name

    def link(self):
        return reverse('recentchanges')

    def description(self):
        return "Recent changes on %s" % self.site().name

    def format_change_set(self, change_obj, change_set):
        for obj in change_set:
            obj.classname = change_obj.classname
            obj.page = change_obj.page(obj)
            obj.title = change_obj.title(obj)
            obj.slug = obj.page.slug
            obj.diff_url = change_obj.diff_url(obj)
            obj.as_of_url = change_obj.as_of_url(obj)
        return change_set

    def items(self):
        change_sets = []

        for change_class in get_changes_classes():
            change_obj = change_class()
            change_set = change_obj.queryset()[:MAX_CHANGES]
            change_sets.append(
                self.format_change_set(change_obj, change_set))

        changes = merge_changes(change_sets)[:MAX_CHANGES]
        return skip_ignored_change_types(changes)

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        user = getattr(item.history_info, 'user', item.history_info.user_ip)
        comment = ''
        change_type = item.history_info.type_verbose().lower()
        if item.history_info.type in REVERTED_TYPES:
            change_type = "%s (to version %s)" % (change_type,
                item.history_info.reverted_to_version.history_info.date)
        if item.history_info.comment:
            comment = ' with comment "%s"' % item.history_info.comment
        return "%s was %s by %s%s." % (item.title, change_type, user, comment)

    def item_link(self, item):
        if item.history_info.type == TYPE_ADDED:
            return item.as_of_url
        if item.history_info.type in [
                TYPE_DELETED, TYPE_DELETED_CASCADE, TYPE_REVERTED_DELETED]:
            return item.get_absolute_url()
        return item.diff_url

    def item_author_name(self, item):
        if item.history_info.user:
            return item.history_info.user.username
        else:
            return item.history_info.user_ip

    def item_author_link(self, item):
        if item.history_info.user:
            return item.history_info.user.get_absolute_url()
        else:
            return ""

    def item_pubdate(self, item):
        return item.history_info.date

    def get_feed(self, obj, request):
        self.request = request
        return super(RecentChangesFeed, self).get_feed(obj, request)

    def _format_pages(self, objs):
        for o in objs:
            o.page = o
            o.title = o.name
            o.diff_view = '%s:compare-dates' % o._meta.app_label
            o.as_of_view = '%s:as_of_date' % o._meta.app_label
        return objs

    def _format_mapdata(self, objs):
        for o in objs:
            o.title = 'Map for "%s"' % o.page.name
            o.slug = o.page.slug
            o.diff_view = '%s:compare-dates' % o._meta.app_label
            o.as_of_view = '%s:as_of_date' % o._meta.app_label
        return objs


class ChangesOnItemFeed(Feed):
    """
    Base class for a changes feed for a single object (a page, map, etc).

    Subclass this -- you can't use it directly.  You need to:

      1. Define get_object().  The object returned should have attributes for:
         page, title, slug.
      2. Define items().  The items returned by items() should have
         attributes for: title, page, diff_view and as_of_view.
    """
    def get_object(self, request, slug):
        raise NotImplementedError(
            "You must subclass ItemChangesFeed and define get_object()")

    def site(self):
        if not hasattr(self, '_current_site'):
            self._current_site = get_current_site(self.request)
        return self._current_site

    def title(self, obj):
        return "Changes for %s on %s" % (obj.title, self.site().name)

    def link(self, obj):
        linkd = obj.get_absolute_url()
        return linkd

    def description(self, obj):
        return "Changes for %s on %s" % (obj.title, self.site().name)

    def items(self, obj):
        raise NotImplementedError(
            "You must subclass ItemChangesFeed and define items()")

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        user = getattr(item.history_info, 'user', item.history_info.user_ip)
        comment = ''
        change_type = item.history_info.type_verbose().lower()
        if item.history_info.type in REVERTED_TYPES:
            change_type = "%s (to version %s)" % (change_type,
                item.history_info.reverted_to_version.history_info.date)
        if item.history_info.comment:
            comment = ' with comment "%s"' % item.history_info.comment
        return "%s was %s by %s%s." % (item.title, change_type, user, comment)

    def item_link(self, item):
        as_of_link = reverse(item.as_of_view, args=(), kwargs={
                'slug': item.page.pretty_slug,
                'date': item.history_info.date}
        )
        diff_link = reverse(item.diff_view, args=(), kwargs={
                'slug': item.page.pretty_slug,
                'date1': item.history_info.date}
        )
        if item.history_info.type == TYPE_ADDED:
            return as_of_link
        if item.history_info.type in [
                TYPE_DELETED, TYPE_DELETED_CASCADE, TYPE_REVERTED_DELETED]:
            return item.get_absolute_url()
        return diff_link

    def item_author_name(self, item):
        if item.history_info.user:
            return item.history_info.user.username
        else:
            return item.history_info.user_ip

    def item_author_link(self, item):
        if item.history_info.user:
            return item.history_info.user.get_absolute_url()
        else:
            return ""

    def item_pubdate(self, item):
        return item.history_info.date

    def get_feed(self, obj, request):
        self.request = request
        return super(ChangesOnItemFeed, self).get_feed(obj, request)


def skip_ignored_change_types(objs):
    return [o for o in objs if o.history_info.type not in IGNORE_TYPES]
