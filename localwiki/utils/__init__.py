from django.utils.functional import lazy
from django.core.urlresolvers import reverse


# TODO: reverse_lazy is defined in Django >= 1.4.  We define it here for
# when Django 1.4 isn't available.
reverse_lazy = lazy(reverse, str)

def after_apps_loaded(f):
    from signals import django_apps_loaded
    def _receiver(sender, *args, **kwargs):
        f()
    django_apps_loaded.connect(_receiver)
