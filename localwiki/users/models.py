import urllib

from django.contrib.auth.models import User
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site

from localwiki.utils.urlresolvers import reverse


#######################################################################
#
#  "Monkey-pathcing is bad, but contib.auth is so badly designed, that
#  using monkey-patching here should be no shame at all."
#
#######################################################################

User._meta.get_field_by_name('email')[0]._unique = True

def name_to_first_last(self, name):
    """
    Takes 'name' and sets self.first_name, self.last_name.

    Args:
        name: A name string.
    """
    split_name = name.split()
    last_name = ''
    if len(split_name) > 1:
        last_name = ' '.join(split_name[1:])
    first_name = split_name[0]

    self.first_name = first_name
    self.last_name = last_name


def first_last_to_name(self):
    name = self.first_name
    if self.last_name:
        name = "%s %s" % (self.first_name, self.last_name)
    return name


def get_absolute_url(self):
    return reverse('user-page', kwargs={'username': smart_str(self.username), 'rest': ''})


User.name = property(first_last_to_name, name_to_first_last)
User.get_absolute_url = get_absolute_url


class UserProfile(models.Model):
    # this field is required
    user = models.OneToOneField(User)
    subscribed = models.BooleanField(verbose_name=_(settings.SUBSCRIBE_MESSAGE), db_index=True)
    _gravatar_email = models.EmailField(verbose_name=_("Gravatar Email (Private)"), max_length=254, blank=True, null=True)
    show_email = models.BooleanField(verbose_name=_("Show email publicly (Helps with communication)"), default=False)
    personal_url = models.URLField(verbose_name=_("Personal website"), blank=True, null=True)

    @property
    def gravatar_email(self):
        return self._gravatar_email or self.user.email


# For registration calls
import signals
