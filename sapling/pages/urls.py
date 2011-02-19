from django.conf.urls.defaults import *
from django.views.generic import ListView

import views
from models import Page

page_list_info = {
    'model': Page,
    'context_object_name': 'page_list',
}

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(**page_list_info), name='title-index'),
    url(r'^(?P<slug>[-\w]+)$', views.PageDetailView.as_view(), name='show-page'),
    url(r'^(?P<slug>[-\w]+)/edit$', views.PageUpdateView.as_view(), name='edit-page'),
    url(r'^(?P<slug>[-\w]+)/upload', views.upload, name='upload-image'),
    url(r'^(?P<slug>[-\w]+)/_history/compare$', views.compare),
    url(r'^(?P<slug>[-\w]+)/_history/(?P<version1>[0-9]+)...(?P<version2>[0-9]+)$', views.compare, name='compare-revisions'),
    url(r'^(?P<slug>[-\w]+)/_history/(?P<version>[0-9]+)$', views.PageVersionDetailView.as_view(), name='page-version'),
    url(r'^(?P<slug>[-\w]+)/_history/$', views.PageHistoryView.as_view(), name='page-history'),
)
