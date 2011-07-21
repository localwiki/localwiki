from models import MapData
from pages.models import Page, slugify

import recentchanges
from recentchanges import RecentChanges
from recentchanges.feeds import ChangesOnItemFeed, MAX_CHANGES
from recentchanges.feeds import skip_ignored_change_types


class MapChanges(RecentChanges):
    classname = 'map'

    def queryset(self, start_at=None):
        if start_at:
            return MapData.history.filter(history_info__date__gte=start_at)
        return MapData.history.all()

    def title(self, obj):
        obj.title = 'Map for "%s"' % obj.page.name

recentchanges.register(MapChanges)


class MapChangesFeed(ChangesOnItemFeed):
    def get_object(self, request, slug):
        # TODO: Break out this MapData-get-page pattern into a function.
        # Non-DRY.
        page = Page(slug=slugify(slug))
        latest_page = page.history.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name

        obj = MapData(page=page)
        obj.page = page
        obj.title = 'Map for "%s"' % obj.page.name
        obj.slug = page.slug
        return obj

    def items(self, obj):
        objs = obj.history.all()[:MAX_CHANGES]
        for o in objs:
            o.title = obj.page.name
            o.diff_view = '%s:compare-dates' % o._meta.app_label
            o.as_of_view = '%s:as_of_date' % o._meta.app_label
        return skip_ignored_change_types(objs)
