from django.core.urlresolvers import reverse as django_reverse
from django.core.urlresolvers import get_urlconf


def reverse(viewname, urlconf=None, args=None, kwargs=None, prefix=None, current_app=None):
    if urlconf is None:
        urlconf = get_urlconf()
        # We behave differently if we're using the no-region urlconf with the
        # no-region django-hosts host.
        if urlconf == 'main.urls_no_region':
            if kwargs and kwargs.get('region'):
                del kwargs['region']

    return django_reverse(viewname, urlconf=urlconf, args=args, kwargs=kwargs, prefix=prefix, current_app=current_app)
