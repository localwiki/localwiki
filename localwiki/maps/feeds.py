from django.utils.translation import ugettext as _
from pages.models import Page, slugify

import activity
from activity import ActivityForModel
from activity.feeds import ChangesOnItemFeed, MAX_CHANGES
from activity.feeds import skip_ignored_change_types

from models import MapData


class MapChanges(ActivityForModel):
    classname = 'map'

    def queryset(self, start_at=None):
        if self.region:
            qs = MapData.versions.filter(region=self.region)
        else:
            qs = MapData.versions.all()

        if start_at:
            qs = qs.filter(version_info__date__gte=start_at)
        return qs

    def title(self, obj):
        return _('Map for "%s"') % obj.page.name

activity.register(MapChanges)


class MapChangesFeed(ChangesOnItemFeed):
    def get_object(self, request, region='', slug=''):
        self.setup_region(region)

        # TODO: Break out this MapData-get-page pattern into a function.
        # Non-DRY.
        page = Page(slug=slugify(slug), region=self.region)
        latest_page = page.versions.most_recent()
        # Need to set the pk on the dummy page for correct MapData lookup.
        page.pk = latest_page.id
        page.name = latest_page.name

        obj = MapData(page=page, region=self.region)
        obj.page = page
        obj.title = _('Map for "%s"') % obj.page.name
        obj.slug = page.slug
        return obj

    def items(self, obj):
        objs = obj.versions.all()[:MAX_CHANGES]
        change_obj = MapChanges()
        change_obj.region = self.region
        for o in objs:
            o.title = obj.page.name
            o.diff_url = change_obj.diff_url(o)
            o.as_of_url = change_obj.as_of_url(o)
        return skip_ignored_change_types(objs)
