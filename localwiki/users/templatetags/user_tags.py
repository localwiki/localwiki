from django import template
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string

from django_gravatar.helpers import get_gravatar_url, has_gravatar

register = template.Library()

@register.simple_tag
def user_link(user, size=20, region=None, show_username=True, ip=None):
    if user and user.is_authenticated():
        # Get twice as big for high-DPI / retina
        gravatar_url = get_gravatar_url(user.userprofile.gravatar_email, size=(size*2))
        user_path = user.get_absolute_url()
        link = """<a href="%(user_path)s" class="user_link" title="%(username)s"><img class="gravatar" src="%(gravatar_url)s" width="%(width)s" height="%(height)s" />%(name)s</a>""" % {
            'user_path': user_path,
            'gravatar_url': gravatar_url,
            'name': (" %s" % user.username) if show_username else "",
            'username': user.username,
            'width': size,
            'height': size,
        }
    elif ip:
        link = ip
    else:
        link = _("Unknown")
    return link

@register.assignment_tag
def user_link_as(user, **kwargs):
    return user_link(user, **kwargs)
