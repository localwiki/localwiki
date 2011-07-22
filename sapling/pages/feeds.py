from models import Page, PageFile, slugify

import recentchanges
from recentchanges import RecentChanges
from recentchanges.feeds import ChangesOnItemFeed

from django.core.urlresolvers import reverse


class PageChanges(RecentChanges):
    classname = 'page'

    def queryset(self, start_at=None):
        if start_at:
            return Page.history.filter(history_info__date__gte=start_at)
        return Page.history.all()

    def page(self, obj):
        return obj


class PageFileChanges(RecentChanges):
    classname = 'file'

    def queryset(self, start_at=None):
        if start_at:
            return PageFile.history.filter(history_info__date__gte=start_at)
        else:
            return PageFile.history.all()

    def page(self, obj):
        try:
            page = Page.objects.get(slug=obj.slug)
        except Page.DoesNotExist:
            page = Page(slug=obj.slug, name=obj.slug.capitalize())
        return page

    def title(self, obj):
        return 'File %s on page "%s"' % (obj.name, self.page(obj).name)

    def diff_url(self, obj):
        return reverse('pages:file-compare-dates', kwargs={
            'slug': self.page(obj).pretty_slug,
            'date1': obj.history_info.date,
            'file': obj.name,
        })

    def as_of_url(self, obj):
        return reverse('pages:file-as_of_date', kwargs={
            'slug': self.page(obj).pretty_slug,
            'date': obj.history_info.date,
            'file': obj.name,
        })


recentchanges.register(PageChanges)
recentchanges.register(PageFileChanges)


class PageChangesFeed(ChangesOnItemFeed):
    recentchanges_class = PageChanges

    def get_object(self, request, slug):
        obj = Page(slug=slugify(slug))
        obj.title = obj.history.most_recent().name
        obj.page = obj
        return obj


class PageFileChangesFeed(ChangesOnItemFeed):
    recentchanges_class = PageFileChanges

    def get_object(self, request, slug='', file=''):
        obj = PageFile(slug=slugify(slug), name=file)
        page = Page(slug=slugify(slug))
        obj.page = page.history.most_recent()
        obj.title = 'File %s on page "%s"' % (obj.name, obj.page.name)
        return obj
