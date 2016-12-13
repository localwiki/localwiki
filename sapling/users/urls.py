from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from registration.views import register

urlpatterns = patterns('',
    url(r'^register/$', register,
        {'backend': 'sapling.users.registration_backend.SaplingBackend'},
        name='registration_register'),
    url(r'^register/closed/$', direct_to_template,
        {'template': 'registration/registration_closed.html'},
        name='registration_disallowed'),
    (r'', include('registration.auth_urls')),
)
