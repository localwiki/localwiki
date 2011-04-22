"""
A simple registration backend for django-registration.
"""
from django.contrib import messages

import registration
from registration.backends.simple import SimpleBackend


class SaplingBackend(SimpleBackend):
    def post_registration_redirect(self, request, user):
        """
        After registration, redirect to the user's account page.
        """
        return ('/pages/Please', (), {})


def registration_complete_msg(sender, user, request, **kwargs):
    messages.add_message(request, messages.SUCCESS,
        "Sign up complete. You are now logged in!")

registration.signals.user_registered.connect(registration_complete_msg)
