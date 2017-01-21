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
