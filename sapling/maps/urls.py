from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^(?P<slug>.+)/_edit/$', views.MapUpdateView.as_view(),
        name='edit-page-map'),
    url(r'^(?P<slug>.+)/_history/compare$', views.MapCompareView.as_view()),
    url(r'^(?P<slug>.+)/_history/(?P<version1>[0-9]+)...(?P<version2>[0-9]+)$',
        views.MapCompareView.as_view(), name='compare-revisions-map'),
    url(r'^(?P<slug>.+)/_history/(?P<version>[0-9]+)$',
        views.MapVersionDetailView.as_view(), name='page-map-version'),
    url(r'^(?P<slug>.+)/_history/$', views.MapHistoryView.as_view(),
        name='page-map-history'),
    url(r'^(?P<slug>.+)/$', views.MapDetailView.as_view(),
        name='show-page-map'),
)
