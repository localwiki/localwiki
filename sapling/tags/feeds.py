from django.core.urlresolvers import reverse

import recentchanges
from recentchanges import RecentChanges

from models import PageTagSet


class PageTagSetChanges(RecentChanges):
    classname = 'tags'

    def queryset(self, start_at=None):
        if start_at:
            return PageTagSet.versions.filter(version_info__date__gte=start_at)
        return PageTagSet.versions.all()

    def page(self, obj):
        return obj.page

    def title(self, obj):
        return 'Tags on page "%s"' % self.page(obj).name

    def diff_url(self, obj):
        return reverse('pages:tags-compare-dates', kwargs={
            'slug': self.page(obj).pretty_slug,
            'date1': obj.version_info.date,
        })

    def as_of_url(self, obj):
        return reverse('pages:tags-as_of_date', kwargs={
            'slug': self.page(obj).pretty_slug,
            'date': obj.version_info.date,
        })

recentchanges.register(PageTagSetChanges)
