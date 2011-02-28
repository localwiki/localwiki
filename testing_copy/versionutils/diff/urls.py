from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^diffs/', include('diffs.foo.urls')),
    (r'^$', 'diffs.diff.views.debug'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
