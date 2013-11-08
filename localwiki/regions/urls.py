from django.conf.urls import *

from regions.views import RegionCreateView, RegionListView, RegionSettingsView


urlpatterns = patterns('',
    url(r'^regions/?', RegionListView.as_view(), name="list"),
    url(r'^_region/_add', RegionCreateView.as_view(), name="add"),
    url(r'^(?P<region>[^/]+?)/_settings/?$', RegionSettingsView.as_view(), name="settings"),
    url(r'^(?P<region>[^/]+?)/_settings/admins/?$', RegionSettingsView.as_view(), name="edit-admins"),
)
