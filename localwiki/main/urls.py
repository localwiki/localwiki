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
from regions.views import MainPageView, RegionCreateView
from users.admin import SubscribedList

from api import api_v2

admin.autodiscover()


urlpatterns = patterns('',
    (r'^/*$', MainPageView.as_view()),
    url(r'^_region/_add', RegionCreateView.as_view(), name="add-region"),
    (r'^api/?$', RedirectView.as_view(url='/api/v2/', query_string=True)),
    url(r'^api/', include(api_v2.urls)),
    (r'^_api/', include('main.api.internal_urls')),
    (r'^(?P<region>[^/]+?)/map/', include(maps.site.urls)),
    (r'^(?P<region>[^/]+?)/tags$', RedirectView.as_view(url='/tags/')),
    (r'^(?P<region>[^/]+?)/tags/', include('tags.urls', 'tags', 'tags')),
    (r'^_redirect/', include(redirects.site.urls)),
    (r'^(?i)Users/', include('users.urls')),
    (r'^(?P<region>[^/]+?)/search/', include('search.urls')),
    (r'^', include('recentchanges.urls')),
    (r'^(?P<region>[^/]+?)/tools/dashboard/', include(dashboard.site.urls)),

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
