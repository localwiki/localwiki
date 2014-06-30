import urllib

from django.template import Library
from django.conf import settings
from django.core.urlresolvers import set_urlconf, get_urlconf, reverse, resolve

from django_hosts.defaults import HOST_SCHEME

register = Library()


@register.simple_tag(takes_context=True)
def render_canonical_url(context, obj=None):
    """
    Returns the canonical URL associated with either the current
    request path or the provided object.
    """
    # A non-request view of some sort
    if not 'request' in context:
        return ''
    if not 'region' in context:
        return ''

    request = context['request']
    region = context['region']

    if obj:
        if request.host.name == settings.DEFAULT_HOST:
            url = obj.get_absolute_url()
            if urllib.unquote(url) == request.path:
                # Don't bother rendering a canonical URL tag.
                return ''
            else:
                return '<link rel="canonical" href="%s" />' % url
        else:
            current_urlconf = get_urlconf()
            set_urlconf(settings.ROOT_URLCONF)
            url = obj.get_absolute_url()
            set_urlconf(current_urlconf)

            url = '%s%s%s' % (HOST_SCHEME, settings.MAIN_HOSTNAME, url)
            return '<link rel="canonical" href="%s" />' % url
    else:
        url = request.path
        if request.host.name == settings.DEFAULT_HOST:
            # We're on the default host, so let's not bother
            # rendering a canonical URL tag.
            return ''
        else:
            # We're on a custom domain, so let's render a URL
            # that points to the main host, but on the same
            # view, args, and kwargs.
            current_urlconf = get_urlconf()

            resolved = resolve(request.path)
            view_name, args, kwargs = resolved.view_name, resolved.args, resolved.kwargs

            set_urlconf(settings.ROOT_URLCONF)

            if 'region' not in kwargs or kwargs['region'] is None:
                kwargs['region'] = region.slug

            # Remove empty kwargs
            kwargs = {k: v for k, v in kwargs.iteritems() if v is not None}

            url = reverse(
                view_name,
                args=args,
                kwargs=kwargs
            )
            set_urlconf(current_urlconf)

            if request.META['QUERY_STRING']:
                qs = '?%s' % request.META['QUERY_STRING']
            else:
                qs = ''
            url = '%s%s%s%s' % (HOST_SCHEME, settings.MAIN_HOSTNAME, url, qs)
            return '<link rel="canonical" href="%s" />' % url
