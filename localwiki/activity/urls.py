from django.conf.urls import *

from localwiki.utils.views import NamedRedirectView

from .views import RegionActivity, FollowedActivity, UserActivity, AllActivity
from .feeds import ActivityFeedSyndication


urlpatterns = patterns('',
    # Changes within a region
    url(r'^(?P<region>[^/]+?)/_activity/?$', RegionActivity.as_view(), name='region-activity'),
    # RSS/Atom feed of changes within a region
    url(r'^(?P<region>[^/]+?)/_activity/_feed/?$', ActivityFeedSyndication(), name='activity-syndication'),

    # Changes made by a particular user 
    url(r'^_activity/users/(?P<username>[^/]+?)/?$', UserActivity.as_view(), name='user-activity'),

    # Changes for -all- of LocalWiki
    url(r'^_activity/?$', AllActivity.as_view(), name='all-activity'),

    ##################################################
    # Legacy URLs for "Recent Changes" URL name here.
    ##################################################

    # Redirect 'Recent_Changes'
    url(r'^(?P<region>[^/]+?)/(?i)Recent_Changes/*$', NamedRedirectView.as_view(name="region-activity", permanent=True)),
    # Redirect RSS/Atom feed of changes within a region
    url(r'^(?P<region>[^/]+?)/(?i)Recent_Changes/_feed/*$', NamedRedirectView.as_view(name="activity-syndication", permanent=True)),
)
