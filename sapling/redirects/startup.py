"""
This module is imported after the server is started. It's intended to be
used regiser request-based startup stuff, like api.register() and feeds.

For non-request based stuff, simply register(), import, etc at the bottom
of a models.py file
"""""


def run():
    import api
    import feeds
