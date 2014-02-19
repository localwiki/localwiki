from django.conf.urls import *

from regions.views import (RegionCreateView, RegionListView, RegionSettingsView,
    RegionAdminsUpdate, RegionBannedUpdate)


urlpatterns = patterns('',
    url(r'^regions/?', RegionListView.as_view(), name="list"),
    url(r'^_region/_add', RegionCreateView.as_view(), name="add"),
    url(r'^(?P<region>[^/]+?)/_settings/?$', RegionSettingsView.as_view(), name="settings"),
    url(r'^(?P<region>[^/]+?)/_settings/admins/?$', RegionAdminsUpdate.as_view(), name="edit-admins"),
    url(r'^(?P<region>[^/]+?)/_settings/banned/?$', RegionBannedUpdate.as_view(), name="edit-banned"),
)
