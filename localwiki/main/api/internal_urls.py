from django.conf.urls import *


urlpatterns = patterns('',
    url(r'^pages/suggest', 'pages.views.suggest'),
    url(r'^tags/suggest/(?P<region>[^/]+?)/?$', 'tags.views.suggest_tags'),
)
