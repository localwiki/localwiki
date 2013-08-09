from django.conf.urls import *

from views import DashboardRenderView, DashboardView

urlpatterns = patterns('',
    url(r'^render', DashboardRenderView.as_view(),
        name="render"),
    url(r'^$', DashboardView.as_view(), name='main'),
)
