from staticfiles.storage import staticfiles_storage


def static_url(path):
    """
    Take a static file path and return the correct URL.

    Simple wrapper around staticfiles.storage.staticfiles_storage.
    """
    return staticfiles_storage.url(path)
