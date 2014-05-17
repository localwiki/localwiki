from django import template
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string

from actstream.models import Action

from activity import get_changes_classes


register = template.Library()

def _date_cmp(x):
    if isinstance(x[0], Action):
        return x[0].timestamp
    return x[0].version_info.date


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

        where each group of [ changes, ..] is grouped by (region, slug).
        The list is ordered by the most recent edit in each
        [changes, ..] list.
    """
    slug_dict = {}
    n_action = 0
    # group changes by slug.
    for change in objs:
        # For Actions, we don't have a slug and we display them
        # differently. So let's index them by a unique, non-slug
        # id (incremented integers)
        if isinstance(change, Action):
            slug_dict[n_action] = [change]
            n_action += 1
        else:
            changes_for_slug = slug_dict.get((change.region, change.slug), [])
            changes_for_slug.append(change)
            slug_dict[(change.region, change.slug)] = changes_for_slug

    # Sort the slug_dict by the most recent edit date of each
    # slug's set of changes.
    by_most_recent_edit = sorted(slug_dict.values(), key=(_date_cmp), reverse=True)
    return by_most_recent_edit


@register.assignment_tag
def format_change_set(changes, region=None):
    changes_classes = get_changes_classes()
    change_obj_for_model = {}
    for _class in changes_classes:
        change_obj = _class(region=region)
        change_obj_for_model[change_obj.queryset().model] = change_obj

    for obj in changes:
        # Skip Action instances - they're displayed differently than
        # versioned changes.
        if isinstance(obj, Action):
            continue

        # Add on the extra formatting attributes we need for fancy
        # template rendering.
        if obj.__class__ not in change_obj_for_model:
            change_obj = change_obj_for_model[obj.__class__.__bases__[0]]
        else:
            change_obj = change_obj_for_model[obj.__class__]
        obj.classname = change_obj.classname
        obj.page = change_obj.page(obj)
        obj.slug = obj.page.slug
        obj.diff_url = change_obj.diff_url(obj)

    return changes
