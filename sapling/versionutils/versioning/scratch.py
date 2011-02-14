import copy

MEMBERS_TO_SKIP = [
    '__dict__',
    '__module__',
    '__weakref__',
    # TODO, maybe: if we wanted to be fancy we could define our
    # own __doc__ that explains "this is like the normal model
    # plus these historical methods"
    '__doc__',
]
def get_all_members(model):
    d = copy.copy(dict(model.__dict__))
    for k in MEMBERS_TO_SKIP:
        if d.get(k, None) is not None:
            del d[k]
    return d
