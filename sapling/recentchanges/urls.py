from django.conf.urls.defaults import *

from views import *


urlpatterns = patterns('',
    url(r'^$', RecentChangesView.as_view(), name='recentchanges'),
)
