from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from rest_framework.routers import DefaultRouter

router = DefaultRouter()


def autoload(submodules):
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        for submodule in submodules:
            try:
                import_module("%s.%s" % (app, submodule))
            except:
                if module_has_submodule(mod, submodule):
                    raise

def load_api_handlers():
    autoload(["api"])
