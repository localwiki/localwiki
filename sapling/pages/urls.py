from django.conf.urls.defaults import *
from django.views.generic import ListView

import views
from models import Page
from pages.models import slugify

page_list_info = {
    'model': Page,
    'context_object_name': 'page_list',
}


def fix_slug(func):
    """
    Applies custom slugify to the slug.
    """
    def wrapped(*args, **kwargs):
        if 'slug' in kwargs:
            kwargs['original_slug'] = kwargs['slug']
            kwargs['slug'] = slugify(kwargs['slug'])
        return func(*args, **kwargs)
    return wrapped


urlpatterns = patterns('',
    url(r'^$', ListView.as_view(**page_list_info), name='title-index'),
    url(r'^(?P<slug>.+)/_edit$', fix_slug(views.PageUpdateView.as_view()),
        name='edit-page'),
    url(r'^(?P<slug>.+)/_upload', fix_slug(views.upload), name='upload-image'),
    url(r'^(?P<slug>.+)/_history/compare$', fix_slug(views.compare)),
    url(r'^(?P<slug>.+)/_history/(?P<version1>[0-9]+)...(?P<version2>[0-9]+)$',
        fix_slug(views.compare), name='compare-revisions'),
    url(r'^(?P<slug>.+)/_history/(?P<version>[0-9]+)$',
        fix_slug(views.PageVersionDetailView.as_view()), name='page-version'),
    url(r'^(?P<slug>.+)/_history/$', fix_slug(views.PageHistoryView.as_view()),
        name='page-history'),
    url(r'^(?P<slug>.+)/$', fix_slug(views.PageDetailView.as_view()),
        name='show-page'),
)
