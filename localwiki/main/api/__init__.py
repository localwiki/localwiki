from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from tastypie.api import Api


api = Api(api_name='v2')

api_v2 = api


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
