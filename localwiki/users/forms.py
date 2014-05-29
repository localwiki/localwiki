from django import forms
from django.utils.translation import ugettext_lazy as _

from regions.fields import UserSetField

from .models import UserProfile


class UserSetForm(forms.Form):
    who_can_change = forms.ChoiceField(
        choices=(
            ('everyone', _('Everyone')),
            ('just_these_users', _('Only these users'))),
        widget=forms.widgets.RadioSelect(),
    )

    def __init__(self, *args, **kwargs):
        region = kwargs.pop('region', None)
        self.this_user = kwargs.pop('this_user', None)
        super(UserSetForm, self).__init__(*args, **kwargs)

        self.fields['users'] = UserSetField(region=region, required=False)


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', '_gravatar_email')

    name = forms.CharField(label=_("Your name"), required=False)
    email = forms.EmailField(label=_("Email address"))
    gravatar_email = forms.EmailField(label=_("Gravatar email (private)"))


class DeactivateForm(forms.Form):
    disabled = forms.BooleanField(initial=False, label=_("Disable this account permanently"))
