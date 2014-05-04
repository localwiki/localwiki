from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from regions.models import Region
from pages.models import Page


class PageSitemap(Sitemap):
    def items(self):
        return Page.objects.defer('content').select_related('region')

    def lastmod(self, obj):
        if not obj.versions.all().exists():
            return

        # Sketchy highly optimized query:
        most_recent = obj.versions.only('history_date')[0]
        return most_recent.history_date


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
