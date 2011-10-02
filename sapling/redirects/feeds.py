from django.core.urlresolvers import reverse

import recentchanges
from recentchanges import RecentChanges

from models import Redirect


class RedirectChanges(RecentChanges):
    classname = 'redirect'

    def queryset(self, start_at=None):
        if start_at:
            return Redirect.versions.filter(version_info__date__gte=start_at)
        else:
            return Redirect.versions.all()

    def page(self, obj):
        from pages.models import Page

        return Page(slug=obj.source, name=obj.source.capitalize())

    def title(self, obj):
        return 'Redirect %s --> %s' % (obj.source, obj.destination)

    def diff_url(self, obj):
        return reverse('redirects:compare-dates', kwargs={
            'slug': obj.source,
            'date1': obj.version_info.date,
        })

    def as_of_url(self, obj):
        # Don't bother.  Just return the source URL.
        return reverse('pages:show', kwargs={'slug': obj.source})

recentchanges.register(RedirectChanges)
