from django.conf.urls.defaults import *
from django.views.generic import list_detail

import views
from models import Page

page_info = {
    'queryset': Page.objects.all(),
    'template_name': 'mikepages/page_list.html',
    'template_object_name': 'page',
}

urlpatterns = patterns('',
    # Example:
    # (r'^diffs/', include('diffs.foo.urls')),
    url(r'^$', list_detail.object_list, page_info, 'title-index'),
    url(r'^(?P<slug>[-\w]+)$', views.show, name='show-page'),
    url(r'^(?P<slug>[-\w]+)/edit$', views.edit, name='edit-page'),
)
