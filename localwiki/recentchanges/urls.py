from django.conf.urls import *

from views import *
from feeds import RecentChangesFeed


urlpatterns = patterns('',
    url(r'^(?P<region>[^/]+?)/(?i)Recent_Changes/*$', RecentChangesView.as_view(),
        name='recentchanges'),
    url(r'^(?P<region>[^/]+?)/(?i)Recent_Changes/_feed/*$', RecentChangesFeed(),
        name='recentchanges-feed'),
)
