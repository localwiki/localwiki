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
)
