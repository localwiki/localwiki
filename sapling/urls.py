from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

import pages
import maps

admin.autodiscover()


urlpatterns = patterns('',
    (r'^pages/', include(pages.site.urls)),
    (r'^map/', include(maps.site.urls)),
    (r'^users/', include('sapling.users.urls')),
    (r'^search/', include('sapling.search.urls')),
    (r'^recent_changes/*', include('sapling.recentchanges.urls')),

    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
