from django.core.urlresolvers import reverse as django_reverse
from django.core.urlresolvers import get_urlconf, NoReverseMatch
from django.conf import settings

from django_hosts.reverse import reverse_full


def reverse(viewname, urlconf=None, args=None, kwargs=None, prefix=None, current_app=None):
    original_kwargs = kwargs
    if urlconf is None:
        urlconf = get_urlconf()
        # We behave differently if we're using the no-region urlconf with the
        # no-region django-hosts host.
        if urlconf == 'main.urls_no_region':
            if kwargs and kwargs.get('region'):
                del kwargs['region']
    try:
        return django_reverse(viewname, urlconf=urlconf, args=args, kwargs=kwargs, prefix=prefix, current_app=current_app)
    except NoReverseMatch as e:
        if urlconf == 'main.urls_no_region':
            # Try the base urlconf and original kwargs
            host = settings.DEFAULT_HOST
            return reverse_full(host, viewname, view_args=args, view_kwargs=original_kwargs)
        else:
            raise e
