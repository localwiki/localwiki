from django.conf.urls.defaults import *
from django.views.generic import list_detail

import views
from models import Page

page_info = {
    'queryset': Page.objects.all(),
    'template_name': 'mikepages/page_list.html',
    'template_object_name': 'page',
}

pages = {
    'queryset': Page.objects.all(),
    'template_object_name': 'page',
}

urlpatterns = patterns('',
    # Example:
    # (r'^diffs/', include('diffs.foo.urls')),
    (r'^$', list_detail.object_list, page_info),
    (r'^(?P<object_id>\d+)/$', list_detail.object_detail, pages),
    (r'^(?P<object_id>\d+)/edit$', views.edit),
    (r'^diff/$', views.diff),
)
