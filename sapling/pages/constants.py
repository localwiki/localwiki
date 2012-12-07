from django.core.urlresolvers import reverse

_base_path = None


def page_base_path():
    global _base_path
    if not _base_path:
        _base_path = reverse('pages:show', args=['foobar'])[:-6]
    return _base_path
