from django.utils.functional import lazy
from django.core.urlresolvers import reverse

from staticfiles.storage import staticfiles_storage


def static_url(path):
    """
    Take a static file path and return the correct URL.

    Simple wrapper around staticfiles.storage.staticfiles_storage.
    """
    try:
        return staticfiles_storage.url(path)
    except ValueError:
        # URL couldn't be found.  Let's just return the path.
        return path


# TODO: reverse_lazy is defined in Django >= 1.4.  We define it here for
# when Django 1.4 isn't available.
reverse_lazy = lazy(reverse, str)
