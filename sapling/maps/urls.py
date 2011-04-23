from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^(?P<slug>.+)/_edit/$', views.MapUpdateView.as_view(),
        name='edit-mapdata'),
    url(r'^(?P<slug>.+)/_delete$', views.MapDeleteView.as_view(),
        name='delete-mapdata'),
    url(r'^(?P<slug>.+)/_revert/(?P<version>[0-9]+)$',
        views.MapRevertView.as_view(), name='revert-mapdata'),
    url(r'^(?P<slug>.+)/_history/compare$', views.MapCompareView.as_view()),
    url(r'^(?P<slug>.+)/_history/(?P<version1>[0-9]+)...(?P<version2>[0-9]+)$',
        views.MapCompareView.as_view(), name='compare-revisions-mapdata'),
    url(r'^(?P<slug>.+)/_history/(?P<version>[0-9]+)$',
        views.MapVersionDetailView.as_view(), name='mapdata-version'),
    url(r'^(?P<slug>.+)/_history/$', views.MapHistoryList.as_view(),
        name='mapdata-history'),
    url(r'^(?P<slug>.+)/$', views.MapDetailView.as_view(),
        name='show-mapdata'),
)
