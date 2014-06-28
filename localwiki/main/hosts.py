from django.conf import settings

from django_hosts import patterns, host

def fix_s(s):
    return s.replace('.', '\.')

if settings.CUSTOM_HOSTNAMES:
    domains = '|'.join(['(%s)' % d for d in settings.CUSTOM_HOSTNAMES])

    host_patterns = patterns('',
        host(domains, 'main.urls_no_region', name='no-region'),
        host(fix_s(settings.MAIN_HOSTNAME), settings.ROOT_URLCONF, name='hub'),
    )
else:
    host_patterns = patterns('',
        host(fix_s(settings.MAIN_HOSTNAME), settings.ROOT_URLCONF, name='hub'),
    )
