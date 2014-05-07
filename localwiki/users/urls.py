from django.conf.urls import *
from django.views.generic import TemplateView 

from registration.views import register

from .views import UserPageView, UserSettingsView, UserDeactivateView, LoginView


urlpatterns = patterns('',
    url(r'^_login/?$', LoginView.as_view(), name="login-main"),
    url(r'^_register/$', register,
        {'backend': 'users.registration_backend.SaplingBackend'},
        name='registration_register'),
    url(r'^_register/closed/$', TemplateView.as_view(
            template_name='registration/registration_closed.html'),
        name='registration_disallowed'),
    url(r'^_settings/?$', UserSettingsView.as_view(), name="user-settings"),
    url(r'^_deactivate/?$', UserDeactivateView.as_view(), name="user-deactivate"),
    (r'', include('registration.auth_urls')),
    (r'(?P<username>[^/]*)/*(?P<rest>.*)', UserPageView.as_view()),
)
