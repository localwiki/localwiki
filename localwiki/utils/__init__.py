from django.utils.functional import lazy
from django.core.urlresolvers import reverse


# TODO: reverse_lazy is defined in Django >= 1.4.  We define it here for
# when Django 1.4 isn't available.
reverse_lazy = lazy(reverse, str)
