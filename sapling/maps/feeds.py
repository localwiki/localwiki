from pages.models import Page, slugify

import recentchanges
from recentchanges import RecentChanges
from recentchanges.feeds import ChangesOnItemFeed, MAX_CHANGES
from recentchanges.feeds import skip_ignored_change_types

from models import MapData


class MapChanges(RecentChanges):
    classname = 'map'

    def queryset(self, start_at=None):
        if start_at:
            return MapData.versions.filter(version_info__date__gte=start_at)
        return MapData.versions.all()

    def title(self, obj):
        return 'Map for "%s"' % obj.page.name

recentchanges.register(MapChanges)


class MapChangesFeed(ChangesOnItemFeed):
    def get_object(self, request, slug):
        # TODO: Break out this MapData-get-page pattern into a function.
        # Non-DRY.
        page = Page(slug=slugify(slug))
        latest_page = page.versions.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name

        obj = MapData(page=page)
        obj.page = page
        obj.title = 'Map for "%s"' % obj.page.name
        obj.slug = page.slug
        return obj

    def items(self, obj):
        objs = obj.versions.all()[:MAX_CHANGES]
        change_obj = MapChanges()
        for o in objs:
            o.title = obj.page.name
            o.diff_url = change_obj.diff_url(o)
            o.as_of_url = change_obj.as_of_url(o)
        return skip_ignored_change_types(objs)
