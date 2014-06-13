import django
from django.db.models.loading import AppCache

django_apps_loaded = django.dispatch.Signal()

def populate_with_signal(cls):
    ret = cls._populate_orig()
    if cls.app_cache_ready():
        if not hasattr(cls, '__signal_sent'):
            cls.__signal_sent = True
            django_apps_loaded.send(sender=None)
    return ret

if not hasattr(AppCache, '_populate_orig'):
    AppCache._populate_orig = AppCache._populate
    AppCache._populate = populate_with_signal


from django.template import add_to_builtins
add_to_builtins('utils.templatetags.smart_url')
