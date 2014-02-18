from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from rest_framework.routers import DefaultRouter
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework import views as rest_framework_views


class APIRoot(rest_framework_views.APIView):
    """
    Welcome to the LocalWiki API!
    
    You're currently browsing the interactive API. You can explore by clicking
    on the links to the various resource endpoints below! Each endpoint has
    associated documentation on its main page.
    
    For more information on interacting with the API, please see the
    **[main API documentation page](http://localwiki.net/main/API_Documentation)**. You will need
    [an API key](http://localwiki.net/main/API_Documentation#api_key) to write using the API.
    """
    _ignore_model_permissions = True
    api_root_dict = {}

    def get(self, request, format=None):
        ret = {}
        for key, url_name in self.api_root_dict.items():
            ret[key] = reverse(url_name, request=request, format=format)
        return Response(ret)


class APIRouter(DefaultRouter):
    """
    Customize DefaultRouter to include our custom documentation.
    """
    def get_api_root_view(self):
        """
        Return a view to use as the API root. Copied from DefaultRouter.
        """
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        APIRoot.api_root_dict = api_root_dict
        return APIRoot().as_view()

router = APIRouter()


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
