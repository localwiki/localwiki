"""
A simple registration backend for django-registration.
"""
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login

import registration
from registration.backends.simple import SimpleBackend

from users.models import name_to_first_last

####
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

attrs_dict = {'class': 'required'}


class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the requested username and email address are not
    already in use.

    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.
    """
    username = forms.RegexField(
        regex=r'^\w+$',
        max_length=30,
        widget=forms.TextInput(attrs=attrs_dict),
        label=_("Username"),
        error_messages={'invalid':
                        _("This value must contain only letters, "
                          "numbers and underscores.")})
    email = forms.EmailField(
        widget=forms.TextInput(attrs=dict(attrs_dict,
                               maxlength=75)),
        label=_("E-mail"))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password"))
    name = forms.CharField(required=False, label=_("Your name"))

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        """
        try:
            User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(
            _("A user with that username already exists."))

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(
                _("This email address is already in use. "
                  "Please supply a different email address."))
        return self.cleaned_data['email']
##


class SaplingBackend(SimpleBackend):
    def post_registration_redirect(self, request, user):
        """
        After registration, redirect to the user's account page.
        """
        return ('/pages/Please', (), {})

    def get_form_class(self, request):
        return RegistrationForm

    def register(self, request, **kwargs):
        user = super(SaplingBackend, self).register(request, **kwargs)
        user.name = kwargs['name']
        user.save()
        return user


def registration_complete_msg(sender, user, request, **kwargs):
    messages.add_message(request, messages.SUCCESS,
        "Sign up complete. You are now logged in!")

registration.signals.user_registered.connect(registration_complete_msg)
