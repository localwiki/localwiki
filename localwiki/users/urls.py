from django.conf.urls import *
from django.views.generic import TemplateView 
from django.contrib.auth import views as auth_views

from registration.views import register

from .views import UserPageView, UserSettingsView, UserDeactivateView, login, logout


urlpatterns = patterns('',
    url(r'^_register/$', register,
        {'backend': 'users.registration_backend.SaplingBackend'},
        name='registration_register'),
    url(r'^_settings/?$', UserSettingsView.as_view(), name="user-settings"),
    url(r'^_deactivate/?$', UserDeactivateView.as_view(), name="user-deactivate"),
    url(r'^login/$', login, {'template_name': 'registration/login.html'},
        name='auth_login'),
    url(r'^logout/$', logout, {'template_name': 'registration/logout.html'},
        name='auth_logout'),
)

# We over-ride the login and logout views, so we just pull in the rest here:
django_registration_urls = patterns('',
    url(r'^password/change/$',
        auth_views.password_change,
        name='auth_password_change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='auth_password_change_done'),
    url(r'^password/reset/$',
        auth_views.password_reset,
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='auth_password_reset_done'),
)

user_page_urls = patterns('',
    url(r'(?P<username>[^/]*)/*(?P<rest>.*)', UserPageView.as_view(), name="user-page"),
)

urlpatterns += django_registration_urls + user_page_urls
