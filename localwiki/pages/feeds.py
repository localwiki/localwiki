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
            return Page.versions.filter(region=self.region, version_info__date__gte=start_at
                ).defer('content')
        return Page.versions.filter(region=self.region).defer('content')

    def page(self, obj):
        return obj

recentchanges.register(PageChanges)


class PageFileChanges(RecentChanges):
    classname = 'file'

    def queryset(self, start_at=None):
        if start_at:
            return PageFile.versions.filter(region=self.region, version_info__date__gte=start_at)
        else:
            return PageFile.versions.filter(region=self.region)

    def page(self, obj):
        try:
            page = Page.objects.get(slug=obj.slug, region=self.region)
        except Page.DoesNotExist:
            page = Page(slug=obj.slug, region=self.region, name=obj.slug.capitalize())
        return page

    def title(self, obj):
        return _('File %(filename)s on page "%(pagename)s"') % {
            'filename': obj.name, 'pagename': self.page(obj).name}

    def diff_url(self, obj):
        return reverse('pages:file-compare-dates', kwargs={
            'slug': self.page(obj).pretty_slug,
            'region': self.region.slug,
            'date1': obj.version_info.date,
            'file': obj.name,
        })

    def as_of_url(self, obj):
        return reverse('pages:file-as_of_date', kwargs={
            'slug': self.page(obj).pretty_slug,
            'region': self.region.slug,
            'date': obj.version_info.date,
            'file': obj.name,
        })


recentchanges.register(PageFileChanges)


class PageChangesFeed(ChangesOnItemFeed):
    recentchanges_class = PageChanges

    def get_object(self, request, region='', slug=''):
        self.setup_region(region)

        obj = Page(slug=slugify(slug), region=self.region)
        obj.title = obj.versions.most_recent().name
        obj.page = obj
        return obj


class PageFileChangesFeed(ChangesOnItemFeed):
    recentchanges_class = PageFileChanges

    def get_object(self, request, region='', slug='', file=''):
        self.setup_region(region)

        obj = PageFile(slug=slugify(slug), region=self.region, name=file)
        page = Page(slug=slugify(slug), region=self.region)
        obj.page = page.versions.most_recent()
        obj.title = _('File %(filename)s on page "%(pagename)s"') % {
            'filename': obj.name, 'pagename': obj.page.name}
        return obj
