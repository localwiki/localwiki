from django.conf.urls.defaults import *

from views import *
from feeds import RecentChangesFeed


urlpatterns = patterns('',
    url(r'^(?i)Recent_Changes/*$', RecentChangesView.as_view(),
        name='recentchanges'),
    url(r'^(?i)Recent_Changes/_feed/*$', RecentChangesFeed(),
        name='recentchanges-feed'),
)
