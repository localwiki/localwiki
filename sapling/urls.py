from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^pages/', include('sapling.pages.urls')),
    (r'^admin/', include(admin.site.urls)),
)
