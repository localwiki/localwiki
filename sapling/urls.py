from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

import pages
import maps

admin.autodiscover()

urlpatterns = patterns('',
    (r'^map/', include(maps.site.urls)),
    (r'^(?i)Users/', include('sapling.users.urls')),
    (r'^search/', include('sapling.search.urls')),
    (r'^', include('sapling.recentchanges.urls')),
    (r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# This should only happen if you're using the local dev server with
# DEBUG=False.
if not settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
    )

# Fall back to pages.
urlpatterns += patterns('',
    (r'^', include(pages.site.urls)),
)
