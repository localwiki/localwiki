from django.views.generic import ListView

from pages.models import Page
from maps.models import MapData


class RecentChangesView(ListView):
    template_name = "recentchanges/recentchanges.html"
    context_object_name = 'change_list'

    def get_queryset(self):
        mapchanges = list(MapData.history.all())
        for o in mapchanges:
            o.pretty_slug = o.page.pretty_slug
            o.name = o.page.name
        pagechanges = list(Page.history.all())

        objs = mapchanges + pagechanges
        for o in objs:
            o.diff_view = '%s:compare-dates' % o._meta.app_label
        return objs
