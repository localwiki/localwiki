from django import template
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string

register = template.Library()

@register.assignment_tag
def group_changes_by_slug(objs):
    """
    Returns:
        A list of the form:
        [
           [ changes, changes, ... ],
           [ changes, changes, ... ],
           ...
        ]

        where each group of [ changes, ..] is grouped by slug.
        The list is ordered by the most recent edit in each
        [changes, ..] list.
    """
    slug_dict = {}
    # group changes by slug.
    for change in objs:
        changes_for_slug = slug_dict.get(change.slug, [])
        changes_for_slug.append(change)
        slug_dict[change.slug] = changes_for_slug

    # Sort the slug_dict by the most recent edit date of each
    # slug's set of changes.
    by_most_recent_edit = sorted(slug_dict.values(),
        key=lambda x: x[0].version_info.date, reverse=True)

    return by_most_recent_edit
