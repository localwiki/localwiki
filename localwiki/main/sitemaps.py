from collections import namedtuple

from django.contrib.sitemaps import Sitemap
from django.db import connection
from django.core.urlresolvers import reverse

from regions.models import Region
from pages.models import Page, page_url


def pages_with_last_mod():
    # We have a lot of pages, and the naive way
    # to generate a sitemap here takes like 5 minutes.
    # This is much faster.
    cursor = connection.cursor()
    cursor.execute("""
SELECT pages_page.name, regions_region.slug, p_by_date.history_date FROM (
    SELECT
        slug, max(history_date) as history_date, region_id
    FROM
        pages_page_hist
    GROUP BY
        slug, region_id
) as p_by_date, pages_page, regions_region
WHERE
    p_by_date.slug=pages_page.slug AND
    p_by_date.region_id=pages_page.region_id AND
    regions_region.id=p_by_date.region_id
""")
    return cursor.fetchall()

MockRegion = namedtuple('MockRegion', ['slug'])

class PageSitemap(Sitemap):
    def items(self):
        items = []
        self.lastmod_lookup = {}
        
        for pagename, region_slug, lastmod in pages_with_last_mod():
            self.lastmod_lookup[(pagename, region_slug)] = lastmod
            items.append((pagename, region_slug))
        return items

    def lastmod(self, obj):
        return self.lastmod_lookup[obj]

    def location(self, obj):
        pagename, region_slug = obj
        # Sort of a mock here.
        return page_url(pagename, MockRegion(region_slug))
        

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
