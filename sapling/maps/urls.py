from django.conf.urls.defaults import *
from django.views.generic import ListView

import views
from models import MapData
from pages.models import slugify

urlpatterns = patterns('',
    #url(r'^$', ListView.as_view(**map_list_info), name='map-index'),
    url(r'^(?P<slug>.+)/_edit/$', views.MapUpdateView.as_view(),
        name='edit-page-map'),
    
    url(r'^(?P<slug>.+)/_history/compare$', views.compare),
    url(r'^(?P<slug>.+)/_history/(?P<version1>[0-9]+)...(?P<version2>[0-9]+)$',
        views.compare, name='compare-revisions-map'),
    # XXX FIX BELOW TO USE verisondetail
    url(r'^(?P<slug>.+)/_history/(?P<version>[0-9]+)$',
        views.MapVersionDetailView.as_view(), name='page-map-version'),
    url(r'^(?P<slug>.+)/_history/$', views.MapHistoryView.as_view(),
        name='page-map-history'),
    #url(r'^(?P<slug>.+)/$', fix_slug(views.PageDetailView.as_view()),
    #    name='show-page'),
    url(r'^(?P<slug>.+)/$', views.MapDetailView.as_view(),
        name='show-page-map'),
)
