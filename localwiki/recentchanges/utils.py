from collections import Counter, defaultdict
import itertools


def merge_changes(objs_lists):
    """
    Given a list of arguments (*objs_lists), each of which is an iterable
    of historical objects, we return an iterable of the provided
    objs_lists combined and sorted by edit date (most recent edits appearing
    earlier in the list).
    """
    # In theory we could use the fact each obj_list is already sorted.
    # This is fast enough for now.  heapq.merge does this, but it
    # doesn't take a key parameter.
    return sorted(itertools.chain(*objs_lists),
                  key=lambda x: x.version_info.date, reverse=True)


def take_n_from(lists_with_indexes, n, merge_key=None):
    """
    Args:
        lists_with_indexes: A tuple of (list, starting_index), e.g.:
            ((pages, pages_i), (maps, maps_i), (files, files_i))

        n: Number of items to take from lists_with_indexes.

        merge_key: Key to use for comparison while doing the list merge.
            Defaults to the usual python comparison.

    Returns:
        A tuple, (items, indexes), where `items` is the n elements,
        taken from a sorted-merge of the input lists, and `indexes`
        are the new indexes for each list after taking `n` elements
        from the merged list.
    """
    def _merge(objs_lists, key=None):
        return sorted(itertools.chain(*objs_lists), key=key, reverse=True)

    max_lists = []
    for (list_num, (l, start_at)) in enumerate(lists_with_indexes):
        # We need the `list_num` to keep track of which elements came
        # from which list.
        l_max = [(x, list_num) for x in l[start_at:n]]
        max_lists.append(l_max)

    # Merge together the lists
    merged_with_list_nums = _merge(max_lists)
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

    return (items, indexes)
