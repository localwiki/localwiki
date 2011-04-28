from heapq import merge

from django.views.generic import ListView

from pages.models import Page
from maps.models import MapData


class RecentChangesView(ListView):
    template_name = "recentchanges/recentchanges.html"
    context_object_name = 'changes_grouped_by_slug'

    def get_queryset(self):
        mapchanges = list(MapData.history.all())
        for o in mapchanges:
            o.slug = o.page.slug
            o.pretty_slug = o.page.pretty_slug
            o.name = o.page.name
        pagechanges = list(Page.history.all())

        # Merge the two sorted-by-date querysets.
        objs = merge(pagechanges, mapchanges)

        slug_dict = {}
        # objs is currently ordered by date.  Group together by slug.
        for obj in objs:
            # For use in the template.
            obj.diff_view = '%s:compare-dates' % obj._meta.app_label

            changes_for_slug = slug_dict.get(obj.slug, [])
            changes_for_slug.append(obj)
            slug_dict[obj.slug] = changes_for_slug

        # Sort the grouped slugs by the first date in the slug's change
        # list.
        objs_by_slug = sorted(slug_dict.values(),
               key=lambda x: x[0].history_info.date, reverse=True)
        return objs_by_slug
