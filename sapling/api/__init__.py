from django.conf.urls.defaults import *

from tastypie.api import Api, AcceptHeaderRouter


api_router = AcceptHeaderRouter()
api = Api(api_name='v1')
api_router.register(api, default=True)
