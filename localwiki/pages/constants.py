from localwiki.utils.urlresolvers import reverse, get_urlconf


def page_base_path(region):
    # Django caches repeated resolver lookups, so this should be
    # pretty fast.
    return reverse('pages:show', kwargs={'region': region.slug, 'slug': 'foobar'})[:-6]
