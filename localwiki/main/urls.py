from django.conf.urls import *
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic import RedirectView 
from django.contrib.admin.views.decorators import staff_member_required

import pages
import maps
import redirects
import dashboard
from users.admin import SubscribedList

from api import api_router

admin.autodiscover()


urlpatterns = patterns('',
    (r'^api$', RedirectView.as_view(url='/api/')),
    url(r'^api/(?P<rest>.*)', api_router.as_view(), name="api"),
    (r'^map/', include(maps.site.urls)),
    (r'^tags$', RedirectView.as_view(url='/tags/')),
    (r'^tags/', include('tags.urls', 'tags', 'tags')),
    (r'^_redirect/', include(redirects.site.urls)),
    (r'^(?i)Users/', include('users.urls')),
    (r'^search/', include('search.urls')),
    (r'^', include('recentchanges.urls')),
    (r'^tools/dashboard/', include(dashboard.site.urls)),

    # JS i18n support.
    (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),

    (r'^admin$', RedirectView.as_view(url='/admin/')),
    (r'^admin/subscribers/$', staff_member_required(SubscribedList.as_view())),
    (r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# This should only happen if you're using the local dev server with
# DEBUG=False.
if not settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    )

# Fall back to pages.
urlpatterns += patterns('',
    (r'^', include(pages.site.urls)),
)
