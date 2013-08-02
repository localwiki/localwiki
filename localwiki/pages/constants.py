from django.core.urlresolvers import reverse

_base_path = None


def page_base_path(region):
    global _base_path
    if not _base_path:
        _base_path = reverse('pages:show', args=[region.slug, 'foobar'])[:-6]
    return _base_path
