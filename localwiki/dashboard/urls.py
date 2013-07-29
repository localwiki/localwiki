from django.conf.urls import *
from django.views.generic import TemplateView

from views import DashboardView

urlpatterns = patterns('',
    url(r'^render', DashboardView.as_view(),
        name="render"),
    url(r'^$',
        TemplateView.as_view(template_name='dashboard/index.html'),
        name='main'),
)
