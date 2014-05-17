from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

import activity
from activity import ActivityForModel

from models import Redirect


class RedirectChanges(ActivityForModel):
    classname = 'redirect'
    page_slug_attribute_name = 'source'

    def queryset(self, start_at=None):
        if self.region:
            qs = Redirect.versions.filter(region=self.region)
        else:
            qs = Redirect.versions.all()

        if start_at:
            qs = qs.filter(version_info__date__gte=start_at)
        return qs

    def page(self, obj):
        from pages.models import Page

        return Page(slug=obj.source, region=obj.region, name=obj.source.capitalize())

    def title(self, obj):
        return _('Redirect %(objsrc)s --> %(objdest)s') % {
                'objsrc':obj.source, 'objdest':obj.destination}

    def diff_url(self, obj):
        return reverse('redirects:compare-dates', kwargs={
            'slug': obj.source,
            'region': obj.region.slug,
            'date1': obj.version_info.date,
        })

    def as_of_url(self, obj):
        # Don't bother.  Just return the source URL.
        return reverse('pages:show', kwargs={'slug': obj.source, 'region': obj.region.slug})

activity.register(RedirectChanges)
