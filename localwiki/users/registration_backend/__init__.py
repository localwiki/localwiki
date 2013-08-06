"""
A simple registration backend for django-registration.
"""
import re
from urlparse import urlparse, parse_qs

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

import registration
from registration.backends.simple import SimpleBackend

from forms import RegistrationForm
from django.conf import settings
from django.contrib.auth.models import Group


class SaplingBackend(SimpleBackend):
    def post_registration_redirect(self, request, user):
        if self._redirect_to == reverse('auth_login'):
            # They clicked "login" and then clicked "register," so
            # let's redirect to the front page.
            self._redirect_to = '/'
        return (self._redirect_to, (), {})

    def get_form_class(self, request):
        return RegistrationForm

    def register(self, request, **kwargs):
        self._redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
        user = super(SaplingBackend, self).register(request, **kwargs)
        user.name = kwargs['name']
        all_group, created = Group.objects.get_or_create(
                                            name=settings.USERS_DEFAULT_GROUP)
        user.groups.add(all_group)
        user.save()
        profile = user.get_profile()
        profile.subscribed = kwargs.get('subscribed', False)
        profile.save()
        return user

region_routing_pattern = re.compile(
    '^/(?P<region>[^/]+?)/.*'
)


def registration_complete_msg(sender, user, request, **kwargs):
    qs = parse_qs(urlparse(request.get_full_path()).query)
    re_match = region_routing_pattern.match(qs['next'][0])
    region_slug = re_match.group('region')

    user_slug = 'Users/%s' % user.username
    users_edit_url = reverse('pages:edit', kwargs={'slug': user_slug, 'region': region_slug})
    messages.add_message(request, messages.SUCCESS,
        _('You are signed up and logged in!'))
    messages.add_message(request, messages.SUCCESS,
        _('Tell us who you are by '
           '<a href="%s">creating a page for yourself!</a>') %
        users_edit_url)

registration.signals.user_registered.connect(registration_complete_msg,
    dispatch_uid='registration_complete_msg')
