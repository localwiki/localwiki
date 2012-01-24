from django.conf.urls.defaults import *

from views import DashboardView

urlpatterns = patterns('',
    url(r'^dashboard',
        DashboardView.as_view(), name='dashboard'),
)
