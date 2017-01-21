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
