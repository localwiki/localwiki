from django.conf.urls.defaults import *
from django.views.generic import list_detail

import views
from models import Page

page_info = {
    'queryset': Page.objects.all(),
    'template_name': 'page_list.html',
    'template_object_name': 'page',
}


urlpatterns = patterns('',
    # Example:
    # (r'^diffs/', include('diffs.foo.urls')),
    (r'^$', list_detail.object_list, page_info),
    (r'^diff/$', views.diff),
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
