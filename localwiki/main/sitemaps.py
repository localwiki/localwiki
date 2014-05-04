from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from regions.models import Region
from pages.models import Page


class PageSitemap(Sitemap):
    def items(self):
        return Page.objects.all()

    def lastmod(self, obj):
        if not obj.versions.all().count():
            return
        most_recent = obj.versions.most_recent()
        return most_recent.version_info.date


class RegionSitemap(Sitemap):
    def items(self):
        return Region.objects.all().exclude(is_active=False)


class StaticViewSitemap(Sitemap):
    def items(self):
        return [
            'main-page',
        ]

    def location(self, item):
        return reverse(item)


sitemaps = {
    'pages': PageSitemap,
    'regions': RegionSitemap,
    'misc_static': StaticViewSitemap,
}
