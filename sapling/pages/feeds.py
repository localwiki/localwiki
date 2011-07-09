from models import Page, PageFile, slugify

import recentchanges
from recentchanges import RecentChanges
from recentchanges.feeds import ChangesOnItemFeed, MAX_CHANGES
from recentchanges.feeds import skip_ignored_change_types

from django.core.urlresolvers import reverse


class PageChanges(RecentChanges):
    classname = 'page'

    def queryset(self, start_at):
        return Page.history.filter(history_info__date__gte=start_at)

    def page(self, obj):
        return obj


class PageFileChanges(RecentChanges):
    classname = 'file'

    def queryset(self, start_at):
        return PageFile.history.filter(history_info__date__gte=start_at)

    def page(self, obj):
        try:
            page = Page.objects.get(slug=obj.slug)
        except Page.DoesNotExist:
            page = Page(slug=obj.slug, name=obj.slug.capitalize())
        return page

    def diff_url(self, obj):
        return reverse('pages:file-compare-dates', kwargs={
            'slug': self.page(obj).pretty_slug,
            'date1': obj.history_info.date,
            'file': obj.name,
        })


recentchanges.register(PageChanges)
recentchanges.register(PageFileChanges)


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
