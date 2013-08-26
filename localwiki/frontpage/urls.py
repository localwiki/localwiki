from django.conf.urls import *

from views import FrontPageView, CoverUploadView

urlpatterns = patterns('',
    url(r'^$', FrontPageView.as_view(), name="frontpage"),
    url(r'^_coverphoto', CoverUploadView.as_view(), name="coverphoto_upload"),
)
