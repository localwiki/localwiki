from django.conf import settings

from django_hosts import patterns, host


host_patterns = patterns('',
    host(r'dev2\.localhost:8082', 'main.urls_no_region', name='no-region'),
    host(r'dev\.localhost:8082', settings.ROOT_URLCONF, name='hub'),
)
