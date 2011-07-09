from django.core.urlresolvers import reverse


class RecentChanges(object):
    classname = None

    def queryset(self, start_at):
        pass

    def page(self, obj):
        return obj.page

    def diff_url(self, obj):
        return reverse('%s:compare-dates' % obj._meta.app_label, kwargs={
            'slug': self.page(obj).pretty_slug,
            'date1': obj.history_info.date,
        })
