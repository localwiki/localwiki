from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

import recentchanges
from recentchanges import RecentChanges
from recentchanges.feeds import ChangesOnItemFeed

from models import Page, PageFile, slugify


class PageChanges(RecentChanges):
    classname = 'page'

    def queryset(self, start_at=None):
        if start_at:
            return Page.versions.filter(version_info__date__gte=start_at
                ).defer('content')
        return Page.versions.all().defer('content')

    def page(self, obj):
        return obj

recentchanges.register(PageChanges)


class PageFileChanges(RecentChanges):
    classname = 'file'

    def queryset(self, start_at=None):
        if start_at:
            return PageFile.versions.filter(version_info__date__gte=start_at)
        else:
            return PageFile.versions.all()

    def page(self, obj):
        try:
            page = Page.objects.get(slug=obj.slug)
        except Page.DoesNotExist:
            page = Page(slug=obj.slug, name=obj.slug.capitalize())
        return page

    def title(self, obj):
        return _('File %(filename)s on page "%(pagename)s"') % {
            'filename': obj.name, 'pagename': self.page(obj).name}

    def diff_url(self, obj):
        return reverse('pages:file-compare-dates', kwargs={
            'slug': self.page(obj).pretty_slug,
            'date1': obj.version_info.date,
            'file': obj.name,
        })

    def as_of_url(self, obj):
        return reverse('pages:file-as_of_date', kwargs={
            'slug': self.page(obj).pretty_slug,
            'date': obj.version_info.date,
            'file': obj.name,
        })


recentchanges.register(PageFileChanges)


class PageChangesFeed(ChangesOnItemFeed):
    recentchanges_class = PageChanges

    def get_object(self, request, slug):
        obj = Page(slug=slugify(slug))
        obj.title = obj.versions.most_recent().name
        obj.page = obj
        return obj


class PageFileChangesFeed(ChangesOnItemFeed):
    recentchanges_class = PageFileChanges

    def get_object(self, request, slug='', file=''):
        obj = PageFile(slug=slugify(slug), name=file)
        page = Page(slug=slugify(slug))
        obj.page = page.versions.most_recent()
        obj.title = _('File %(filename)s on page "%(pagename)s"') % {
            'filename': obj.name, 'pagename': obj.page.name}
        return obj
