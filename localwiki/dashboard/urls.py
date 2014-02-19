from django.conf.urls import *

from views import DashboardRenderView, DashboardView

urlpatterns = patterns('',
    url(r'^(?P<region>([^_][^/]*)?)/?_render', DashboardRenderView.as_view(),
        name="render"),
    url(r'^(?P<region>([^_][^/]*)?)/?$', DashboardView.as_view(), name='main'),
)
