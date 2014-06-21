from django.conf.urls import *
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from django.contrib.admin.views.decorators import staff_member_required

import pages
import maps
import redirects
import dashboard
import regions
from regions.views import MainPageView
from users.views import GlobalUserpageRedirectView
from utils.views import NamedRedirectView
from users.admin import SubscribedList

from api import load_api_handlers
# We load all of the api.py files right now.
# TODO: Change this once Django (1.6?) supports the
# apps_loaded signal.  Right now, we need to do this
# to avoid nasty circular imports.
load_api_handlers()
from api import router

admin.autodiscover()


urlpatterns = patterns('',
    # Follow-related URLs
    (r'^_follow/', include('follow.urls')),
    (r'^_stars/', include('stars.urls')),

    # Region routing URLs
    (r'^', include(regions.site.urls)),
    
    # Internal API URLs
    (r'^_api/', include('main.api.internal_urls')),

    (r'^map$', NamedRedirectView.as_view(name='maps:global')),
    (r'^map/', include(maps.site.urls)),
    (r'^tags$', NamedRedirectView.as_view(name='tags:list')),
    (r'^tags/', include('tags.urls', 'tags', 'tags')),
    (r'^_redirect/', include(redirects.site.urls)),
    (r'^', include('search.urls_no_region')),
    (r'^', include('activity.urls_no_region')),
    (r'^', include('explore.urls')),

    # Region userpage -> global userpage redirect
    (r'^((?i)Users)/(?P<username>[^/]+?)$', GlobalUserpageRedirectView.as_view()),

    # Historical URL for dashboard:
    (r'^tools/dashboard/?$', NamedRedirectView.as_view(name='dashboard:main')),
    (r'^_tools/dashboard/', include(dashboard.site.urls)),

    # JS i18n support.
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog'),

    (r'^(((?i)Front[_ ]Page)/?)?', include('frontpage.urls')),

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
