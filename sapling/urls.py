from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^sapling/', include('sapling.foo.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    (r'^mikepages/', include('sapling.mikepages.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    try:
        urlpatterns += patterns('',
            (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root': settings.MEDIA_ROOT}),
        )
    except:
        pass
