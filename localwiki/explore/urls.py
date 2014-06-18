from django.conf.urls import *

from localwiki.utils.views import NamedRedirectView
from maps.widgets import InfoMap

from .views import RandomExploreList, AlphabeticalExploreList, ExploreJustList


urlpatterns = patterns('',
    url(r'^_explore/?$', RandomExploreList.as_view(), name='explore'),
    url(r'^_explore/alphabetical/?$', AlphabeticalExploreList.as_view(), name='explore-alphabetical'),
    url(r'^_explore/list/?$', ExploreJustList.as_view(), name='explore-as-list'),

    ##########################################################
    # Redirects to preserve old URLs
    ########################################################## 
    url(r'^(?i)All_Pages/*$', NamedRedirectView.as_view(name='explore-as-list')),
)
