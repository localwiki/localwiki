from localwiki.utils.urlresolvers import reverse

import activity
from activity import ActivityForModel

from models import PageTagSet


class PageTagSetChanges(ActivityForModel):
    classname = 'tags'

    def queryset(self, start_at=None):
        if self.region:
            qs = PageTagSet.versions.filter(region=self.region)
        else:
            qs = PageTagSet.versions.all()

        if start_at:
            qs = qs.filter(version_info__date__gte=start_at)
        return qs

    def page(self, obj):
        return obj.page

    def title(self, obj):
        return 'Tags on page "%s"' % self.page(obj).name

    def diff_url(self, obj):
        return reverse('pages:tags-compare-dates', kwargs={
            'slug': self.page(obj).pretty_slug,
            'region': self.page(obj).region.slug,
            'date1': obj.version_info.date,
        })

    def as_of_url(self, obj):
        return reverse('pages:tags-as_of_date', kwargs={
            'slug': self.page(obj).pretty_slug,
            'region': self.page(obj).region.slug,
            'date': obj.version_info.date,
        })

activity.register(PageTagSetChanges)
