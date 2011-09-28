import urllib

from django.contrib.auth.models import User
from django.utils.encoding import smart_str

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
    return "/Users/%s" % urllib.quote(smart_str(self.username))


User.name = property(first_last_to_name, name_to_first_last)
User.get_absolute_url = get_absolute_url
