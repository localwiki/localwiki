from django import template
from django.template.loader import render_to_string

from django_gravatar.helpers import get_gravatar_url, has_gravatar

register = template.Library()

@register.simple_tag
def user_link(user, size=20, region=None, show_username=True, ip=None):
    if user and user.is_authenticated():
        # Get twice as big for high-DPI / retina
        gravatar_url = get_gravatar_url(user.userprofile.gravatar_email, size=(size*2))
        if region:
            user_path= '/%s%s' % (region.slug, user.get_absolute_url())
        else:
            user_path = user.get_absolute_url()
        link = """<a href="%(user_path)s" class="user_link"><img class="gravatar" src="%(gravatar_url)s" width="%(width)s" height="%(height)s" />%(username)s</a>""" % {
            'user_path': user_path,
            'gravatar_url': gravatar_url,
            'username': (" %s" % user.username) if show_username else "",
            'width': size,
            'height': size,
        }
    elif ip:
        link = ip
    return link
