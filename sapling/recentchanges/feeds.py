from django.contrib.syndication.views import Feed
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse

from pages.models import Page
from maps.models import MapData
from versionutils.versioning.constants import *

from utils import merge_changes

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

    def items(self):
        pagechanges = Page.history.all()[:MAX_CHANGES]
        pagechanges = self._format_pages(pagechanges)
        mapchanges = MapData.history.all()[:MAX_CHANGES]
        mapchanges = self._format_mapdata(mapchanges)

        return merge_changes(pagechanges, mapchanges)[:MAX_CHANGES]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        user = getattr(item.history_info, 'user', item.history_info.user_ip)
        comment = ''
        if item.history_info.comment:
            comment = ' with comment "%s"' % item.history_info.comment
        return "%s was %s by %s%s." % (
            item.title, item.history_info.type_verbose().lower(),
            user, comment)

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

      1. Define get_object() and items().
      2. Make sure you set the following attributes on the returned object in
         get_object() as well as on all of the items returned by items():

         title, slug, page, diff_view, as_of_view.
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
        return obj.get_absolute_url()

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
        if item.history_info.comment:
            comment = ' with comment "%s"' % item.history_info.comment
        return "%s was %s by %s%s." % (
            item.title, item.history_info.type_verbose().lower(),
            user, comment)

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
