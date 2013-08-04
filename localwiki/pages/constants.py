from django.core.urlresolvers import reverse


def page_base_path(region):
    # Django caches repeated resolver lookups, so this should be
    # pretty fast.
    return reverse('pages:show', args=[region.slug, 'foobar'])[:-6]
