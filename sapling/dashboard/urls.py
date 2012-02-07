from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from views import DashboardView

urlpatterns = patterns('',
    url(r'^dashboard/render', DashboardView.as_view(),
        name="render"),
    url(r'^dashboard', direct_to_template,
        {'template': 'dashboard/index.html'}, name='main'),
)
