import itertools
import threading
from collections import Counter, defaultdict

from django.utils.functional import lazy
from django.core.urlresolvers import reverse


# TODO: reverse_lazy is defined in Django >= 1.4.  We define it here for
# when Django 1.4 isn't available.
reverse_lazy = lazy(reverse, str)

def after_apps_loaded(f):
    from signals import django_apps_loaded
    def _receiver(sender, *args, **kwargs):
        f()
    django_apps_loaded.connect(_receiver)


def take_n_from(lists_with_indexes, n, merge_key=None):
    """
    Args:
        lists_with_indexes: A tuple of (list, starting_index), e.g.:
            ((pages, pages_i), (maps, maps_i), (files, files_i))

        n: Number of items to take from lists_with_indexes.

        merge_key: Key to use for comparison while doing the list merge.
            Defaults to no comparison / sort (leave in place).

    Returns:
        A tuple, (items, indexes, has_more_left), where `items` is the n elements,
        taken from a sorted-merge of the input lists, and `indexes`
        are the new indexes for each list after taking `n` elements
        from the merged list.  `has_more_left` indicates whether there are more
        elements left to grab beyond those returned.
    """
    def _merge(objs_lists, merge_key=None):
        def _merge_f(x):
            item, index = x
            if not merge_key:
                return None
            return merge_key(item)
        return sorted(itertools.chain(*objs_lists), key=_merge_f, reverse=True)

    has_more_left = False
    max_lists = []
    for (list_num, (l, start_at)) in enumerate(lists_with_indexes):
        # We need the `list_num` to keep track of which elements came
        # from which list.
        _slice = l[start_at:start_at+n]
        l_max = [(x, list_num) for x in _slice]
        if not has_more_left and len(_slice) != len(l[start_at:start_at+n+1]):
            has_more_left = True
        max_lists.append(l_max)

    # Check to see if the sum total of each slice is more than
    # the amount we're asking for.
    if not has_more_left:
        total = 0
        for l in max_lists:
            total += len(l)
        if total > n:
            has_more_left = True

    # Merge together the lists
    merged_with_list_nums = _merge(max_lists, merge_key=merge_key)
    items_with_list_nums = merged_with_list_nums[:n]

    items = []
    n_items_from_each_list = defaultdict(int)
    for (item, list_num) in items_with_list_nums:
        items.append(item)
        # Count the number of items that came from each original list
        n_items_from_each_list[list_num] += 1

    indexes = []
    # Calculate new index for each input list
    for (list_num, (l, start_at)) in enumerate(lists_with_indexes):
        n_from = n_items_from_each_list[list_num]
        indexes.append(start_at + n_from)

    return (items, indexes, has_more_left)


def get_base_uri():
    from .middleware import _threadlocal
    return getattr(_threadlocal, 'base_uri', '')
