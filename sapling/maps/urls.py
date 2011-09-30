from django.conf.urls.defaults import *

from utils.constants import DATETIME_REGEXP
from views import *
from feeds import MapChangesFeed
from maps.views import MapObjectsForBounds

urlpatterns = patterns('',
    url(r'^$', MapGlobalView.as_view(), name='global'),
    url(r'^_objects/$', MapObjectsForBounds.as_view(), name='objects'),
    url(r'^(?P<slug>.+)/_edit$', MapUpdateView.as_view(),  name='edit'),
    url(r'^(?P<slug>.+)/_delete$', MapDeleteView.as_view(), name='delete'),
    url(r'^(?P<slug>.+)/_revert/(?P<version>[0-9]+)$',
        MapRevertView.as_view(), name='revert'),

    url(r'^(?P<slug>.+)/_history/compare$', MapCompareView.as_view()),
    url((r'^(?P<slug>.+)/_history/'
            r'(?P<version1>[0-9]+)\.\.\.(?P<version2>[0-9]+)?$'),
        MapCompareView.as_view(), name='compare-revisions'),
    url(r'^(?P<slug>.+)/_history/(?P<date1>%s)\.\.\.(?P<date2>%s)?$' %
        (DATETIME_REGEXP, DATETIME_REGEXP),
        MapCompareView.as_view(), name='compare-dates'),
    url(r'^(?P<slug>.+)/_history/(?P<version>[0-9]+)$',
        MapVersionDetailView.as_view(), name='as_of_version'),
    url(r'^(?P<slug>.+)/_history/(?P<date>%s)$' % DATETIME_REGEXP,
        MapVersionDetailView.as_view(), name='as_of_date'),
    url(r'^(?P<slug>.+)/_history/_feed/*$', MapChangesFeed(),
        name='changes-feed'),
    url(r'^(?P<slug>.+)/_history/$', MapVersionsList.as_view(),
        name='history'),
    url(r'^(?P<slug>(?:(?!/_).)+?)/*$', MapDetailView.as_view(),
        name='show'),
)
