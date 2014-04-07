from django.conf.urls import *

from .views import FollowedPagesListView, FollowedUsersListView


urlpatterns = patterns('',
    url(r'^_pages/(?P<username>[^/]*)/?', FollowedPagesListView.as_view(), name="followed-pages"),
    url(r'^_users/(?P<username>[^/]*)/?', FollowedUsersListView.as_view(), name="followed-users"),
)
