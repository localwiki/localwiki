from django.conf.urls import *

from .views import RecentChangesView, FollowedActivityFeed
from .feeds import RecentChangesFeed


urlpatterns = patterns('',
    # Changes within a region
    url(r'^(?P<region>[^/]+?)/(?i)Recent_Changes/*$', RecentChangesView.as_view(),
        name='recentchanges'),
    # RSS/Atom feed of changes within a region
    url(r'^(?P<region>[^/]+?)/(?i)Recent_Changes/_feed/*$', RecentChangesFeed(),
        name='recentchanges-feed'),

    # Changes and activity that the user follows
    url(r'^_activity/?$', FollowedActivityFeed.as_view(),
        name='followed-activity-feed'),
)
