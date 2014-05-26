from django.conf.urls import *

from localwiki.utils.views import NamedRedirectView
from maps.widgets import InfoMap

from .views import RandomExploreList, AlphabeticalExploreList, ExploreJustList


urlpatterns = patterns('',
    url(r'^(?P<region>[^/]+?)/_explore/?$', RandomExploreList.as_view(), name='explore'),
    url(r'^(?P<region>[^/]+?)/_explore/alphabetical/?$', AlphabeticalExploreList.as_view(), name='explore-alphabetical'),
    url(r'^(?P<region>[^/]+?)/_explore/list/?$', ExploreJustList.as_view(), name='explore-as-list'),

    ##########################################################
    # Redirects to preserve old URLs
    ########################################################## 
    url(r'^(?P<region>[^/]+?)/(?i)All_Pages/*$', NamedRedirectView.as_view(name='explore-as-list')),
)
