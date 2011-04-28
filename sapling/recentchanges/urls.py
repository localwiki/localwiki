from django.conf.urls.defaults import *

from views import *
from feeds import RecentChangesFeed


urlpatterns = patterns('',
    url(r'^$', RecentChangesView.as_view(), name='recentchanges'),
    url(r'^_feed/*$', RecentChangesFeed(), name='recentchanges-feed'),
)
