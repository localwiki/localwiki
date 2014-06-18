from django.conf.urls import *

from localwiki.utils.views import NamedRedirectView

from .views import RegionActivity, FollowedActivity, UserActivity, AllActivity
from .feeds import ActivityFeedSyndication


urlpatterns = patterns('',
    # Changes within a region
    url(r'^_activity/?$', RegionActivity.as_view(), name='region-activity'),

    ##################################################
    # Legacy URLs for "Recent Changes" URL name here.
    ##################################################

    # Redirect 'Recent_Changes'
    url(r'^(?i)Recent_Changes/*$', NamedRedirectView.as_view(name="region-activity", permanent=True)),
)
