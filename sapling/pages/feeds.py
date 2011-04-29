from models import Page, slugify

from recentchanges.feeds import ChangesOnItemFeed, MAX_CHANGES
from recentchanges.feeds import skip_ignored_change_types


class PageChangesFeed(ChangesOnItemFeed):
    def get_object(self, request, slug):
        obj = Page(slug=slugify(slug))
        obj .title = obj.history.most_recent().name
        obj.page = obj
        return obj

    def items(self, obj):
        objs = obj.history.all()[:MAX_CHANGES]
        for o in objs:
            o.title = o.name
            o.page = o
            o.diff_view = '%s:compare-dates' % o._meta.app_label
            o.as_of_view = '%s:as_of_date' % o._meta.app_label
        return skip_ignored_change_types(objs)
