from django.conf.urls.defaults import *
from tags.views import TagListView, TaggedList

urlpatterns = patterns('',
    url(r'^$', TagListView.as_view(), name='list'),
    url(r'^(?P<slug>.+)/*$', TaggedList.as_view(), name='tagged'),
)
