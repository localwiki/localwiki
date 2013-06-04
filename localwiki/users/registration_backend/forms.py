import re

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.safestring import mark_safe

from users.models import UserProfile

attrs_dict = {'class': 'required'}

# We don't allow certain characters in usernames
username_regex = re.compile(r'^[\w0-9.+-]+$', re.UNICODE)


class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the requested username and email address are not
    already in use.  Also presents a checkbox to agree to Terms of Service.

    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.
    """
    username = forms.RegexField(
        regex=username_regex,
        max_length=30,
        widget=forms.TextInput(attrs=attrs_dict),
        label=_("Username"),
        error_messages={'invalid':
                        _("This value may contain only letters (a-z), "
                          "numbers, +, - and .")})
    email = forms.EmailField(
        widget=forms.TextInput(attrs=dict(attrs_dict,
                               maxlength=75)),
        label=_("E-mail"))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password"))
    name = forms.CharField(required=False, label=_("Your name"))

    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
            label=mark_safe(_(settings.SIGNUP_TOS)),
            error_messages={'required':
                _("You must agree to the terms to register")})

    subscribed = UserProfile._meta.get_field('subscribed').formfield()


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
