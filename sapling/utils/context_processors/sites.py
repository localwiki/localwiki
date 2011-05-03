from django.contrib.sites.models import get_current_site


def current_site(request):
    """
    Context processor add get_current_site() as {{{ current_site }}} to
    template context.
    """
    return {'current_site': get_current_site(request)}
