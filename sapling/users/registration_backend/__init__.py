"""
A simple registration backend for django-registration.
"""
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME

import registration
from registration.backends.simple import SimpleBackend

from forms import RegistrationForm


class SaplingBackend(SimpleBackend):
    def post_registration_redirect(self, request, user):
        return (self._redirect_to, (), {})

    def get_form_class(self, request):
        return RegistrationForm

    def register(self, request, **kwargs):
        self._redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
        user = super(SaplingBackend, self).register(request, **kwargs)
        user.name = kwargs['name']
        user.save()
        return user


def registration_complete_msg(sender, user, request, **kwargs):
    messages.add_message(request, messages.SUCCESS,
        "Sign up complete. You are now logged in!")

registration.signals.user_registered.connect(registration_complete_msg,
    dispatch_uid='registration_complete_msg')
