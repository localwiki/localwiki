from django.conf.urls.defaults import *
from django.views.generic import ListView

import views
import models
from models import Page

page_list_info = {
    'model': Page,
    'context_object_name': 'page_list',
}


def slugify(func):
    """Applies custom slugify to the slug and stashes original slug
    """
    def wrapped(*args, **kwargs):
        if 'slug' in kwargs:
            kwargs['original_slug'] = kwargs['slug']
            kwargs['slug'] = models.slugify(kwargs['slug'])
        return func(*args, **kwargs)
    return wrapped


urlpatterns = patterns('',
    url(r'^$', ListView.as_view(**page_list_info), name='title-index'),
    url(r'^(?P<slug>.+)/_edit$', slugify(views.PageUpdateView.as_view()),
        name='edit-page'),
    url(r'^(?P<slug>.+)/_delete$', slugify(views.PageDeleteView.as_view()),
        name='delete-page'),
    url(r'^(?P<slug>.+)/_revert/(?P<version>[0-9]+)$',
        slugify(views.PageRevertView.as_view()), name='revert-page'),
    url(r'^(?P<slug>.+)/_upload', slugify(views.upload), name='upload-image'),
    url(r'^(?P<slug>.+)/_history/compare$',
        slugify(views.PageCompareView.as_view())),
    url(r'^(?P<slug>.+)/_history/(?P<version1>[0-9]+)...(?P<version2>[0-9]+)$',
        slugify(views.PageCompareView.as_view()), name='compare-revisions'),
    url(r'^(?P<slug>.+)/_history/(?P<version>[0-9]+)$',
        slugify(views.PageVersionDetailView.as_view()), name='page-version'),
    url(r'^(?P<slug>.+)/_history/$', slugify(views.PageHistoryView.as_view()),
        name='page-history'),
    url(r'^(?P<slug>.+)/_files/$', slugify(views.PageFilesView.as_view()),
        name='page-files'),
    url(r'^(?P<slug>.+)/$', slugify(views.PageDetailView.as_view()),
        name='show-page'),
)
