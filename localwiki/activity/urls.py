from django.conf.urls import *

from localwiki.utils.views import NamedRedirectView

from .views import RegionActivity, FollowedActivity
from .feeds import ActivityFeedSyndication


urlpatterns = patterns('',
    # Changes within a region
    url(r'^(?P<region>[^/]+?)/_activity/?$', RegionActivity.as_view(),
        name='region-activity'),
    # RSS/Atom feed of changes within a region
    url(r'^(?P<region>[^/]+?)/_activity/_feed/?$', ActivityFeedSyndication(),
        name='activity-syndication'),

    # Changes and activity that the user follows
    url(r'^_activity/?$', FollowedActivity.as_view(),
        name='followed-activity'),

    ##################################################
    # Legacy URLs for "Recent Changes" URL name here.
    ##################################################

    # Redirect 'Recent_Changes'
    url(r'^(?P<region>[^/]+?)/(?i)Recent_Changes/*$', NamedRedirectView.as_view(name="region-activity", permanent=True)),
    # Redirect RSS/Atom feed of changes within a region
    url(r'^(?P<region>[^/]+?)/(?i)Recent_Changes/_feed/*$', NamedRedirectView.as_view(url="activity-syndication", permanent=True)),
)
