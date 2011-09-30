from django.conf.urls.defaults import *

from utils.constants import DATETIME_REGEXP

from views import RedirectUpdateView, RedirectDeleteView
from views import RedirectCompareView

urlpatterns = patterns('',
    url(r'^(?P<slug>.+)/_delete$',
        RedirectDeleteView.as_view(), name='delete'),
    url(r'^(?P<slug>.+)/_history/(?P<date1>%s)\.\.\.(?P<date2>%s)?$'
        % (DATETIME_REGEXP, DATETIME_REGEXP),
        RedirectCompareView.as_view(), name='compare-dates'),
    url(r'^(?P<slug>.+)/', RedirectUpdateView.as_view(), name='edit'),
        
)
