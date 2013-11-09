from django.conf.urls import *


urlpatterns = patterns('',
    url(r'^pages/suggest', 'pages.views.suggest'),
    url(r'^tags/suggest/(?P<region>[^/]+?)/?$', 'tags.views.suggest_tags'),
    url(r'^users/suggest/(?P<region>[^/]+?)/?$', 'users.views.suggest_users'),
)
