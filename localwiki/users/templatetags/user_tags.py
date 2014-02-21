from django import template
from django.template.loader import render_to_string

from django_gravatar.helpers import get_gravatar_url, has_gravatar

register = template.Library()

@register.simple_tag
def user_link(user, size=20, region=None):
    if user.is_authenticated():
        # Get twice as big for high-DPI / retina
        gravatar_url = get_gravatar_url(user.userprofile.gravatar_email, size=(size*2))
        if region:
            user_path= '/%s%s' % (region.slug, user.get_absolute_url())
        else:
            region_path = user.get_absolute_url()
        link = """<a href="%(user_path)s" class="user_link"><img class="gravatar" src="%(gravatar_url)s" width="%(width)s" height="%(height)s" /> %(username)s</a>""" % {
            'user_path': user_path,
            'gravatar_url': gravatar_url,
            'username': user.username,
            'width': size,
            'height': size,
        }
    else:
        link = "FIXME"
    return link
