from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^mikepages/', include('sapling.mikepages.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    try:
        urlpatterns += patterns('',
            (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root': settings.MEDIA_ROOT,
                         'show_indexes': True}),
        )
    except:
        pass
