from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

import pages
import maps

admin.autodiscover()

urlpatterns = patterns('',
    (r'^map/', include(maps.site.urls)),
    (r'^Users/', include('sapling.users.urls')),
    (r'^search/', include('sapling.search.urls')),
    (r'^', include('sapling.recentchanges.urls')),
    (r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Fall back to pages.
urlpatterns += patterns('',
    (r'^', include(pages.site.urls)),
)
