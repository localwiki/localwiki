from django.core.urlresolvers import reverse

from recentchanges import RecentChanges


class RedirectChanges(RecentChanges):
    classname = 'redirect'

    def queryset(self, start_at=None):
        from models import Redirect

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
        return reverse('pages:redirect-compare-dates', kwargs={
            'slug': obj.source,
            'date1': obj.version_info.date,
        })

    def as_of_url(self, obj):
        # Don't bother.  Just return the source URL.
        return reverse('pages:show', kwargs={'slug': obj.source})
