from django.conf.urls import *
from django.views.generic import TemplateView 

from registration.views import register

from .views import UserPageView, UserSettingsView


urlpatterns = patterns('',
    url(r'^_register/$', register,
        {'backend': 'users.registration_backend.SaplingBackend'},
        name='registration_register'),
    url(r'^_register/closed/$', TemplateView.as_view(
            template_name='registration/registration_closed.html'),
        name='registration_disallowed'),
    url(r'^_settings/?$', UserSettingsView.as_view(), name="user-settings"),
    (r'', include('registration.auth_urls')),
    (r'(?P<username>[^/]*)/*(?P<rest>.*)', UserPageView.as_view()),
)
