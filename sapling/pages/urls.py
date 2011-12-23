from django.conf.urls.defaults import *
from django.views.generic import ListView

from views import *
from feeds import PageChangesFeed, PageFileChangesFeed
import models
from utils.constants import DATETIME_REGEXP
from models import Page
from views import PageFilebrowserView

page_list_info = {
    'model': Page,
    'context_object_name': 'page_list',
    'queryset': Page.objects.all().order_by('name'),
}


def slugify(func):
    """
    Applies custom slugify to the slug and stashes original slug
    """
    def wrapped(*args, **kwargs):
        if 'slug' in kwargs:
            kwargs['original_slug'] = kwargs['slug']
            kwargs['slug'] = models.slugify(kwargs['slug'])
        return func(*args, **kwargs)
    return wrapped


urlpatterns = patterns('',
    ###########################################################
    # Files URLs
    # TODO: break out into separate files app with own URLs
    # TODO: shouldn't some of these be _history and not _info?
    ###########################################################
    url(r'^(?P<slug>.+)/_files/$', slugify(PageFileListView.as_view()),
        name='filelist'),
    url(r'^(?P<slug>.+)/_files/(?P<file>.+)/_revert/(?P<version>[0-9]+)$',
        slugify(PageFileRevertView.as_view()), name='file-revert'),
    url(r'^(?P<slug>.+)/_files/(?P<file>.+)/_upload$',
        slugify(upload), name='file-upload'),
    url(r'^(?P<slug>.+)/_files/(?P<file>.+)/_info/$',
        slugify(PageFileInfo.as_view()), name='file-info'),
    url(r'^(?P<slug>.+)/_files/(?P<file>.+)/_info/_feed/*$',
        PageFileChangesFeed(), name='file-changes-feed'),
    url(r'^(?P<slug>.+)/_files/(?P<file>.+)/_info/compare$',
        slugify(PageFileCompareView.as_view())),
    url((r'^(?P<slug>.+)/_files/(?P<file>.+)/_info/'
            r'(?P<version1>[0-9]+)\.\.\.(?P<version2>[0-9]+)?$'),
        slugify(PageFileCompareView.as_view()), name='file-compare-revisions'),
    url(r'^(?P<slug>.+)/_files/(?P<file>.+)/_info/'
        r'(?P<date1>%s)\.\.\.(?P<date2>%s)?$'
        % (DATETIME_REGEXP, DATETIME_REGEXP),
        slugify(PageFileCompareView.as_view()), name='file-compare-dates'),
    url(r'^(?P<slug>.+)/_files/(?P<file>.+)/_info/(?P<version>[0-9]+)$',
        slugify(PageFileVersionDetailView.as_view()),
        name='file-as_of_version'),
    url(r'^(?P<slug>.+)/_files/(?P<file>.+)/_info/(?P<date>%s)$'
        % DATETIME_REGEXP, slugify(PageFileVersionDetailView.as_view()),
        name='file-as_of_date'),
    url(r'^(?P<slug>.+)/_files/(?P<file>.+)$', slugify(PageFileView.as_view()),
        name='file'),
    url(r'^(?P<slug>.+)/_upload', slugify(upload), name='upload-image'),
    url(r'^(?P<slug>.+)/_filebrowser/(?P<filter>(files|images))$',
        slugify(PageFilebrowserView.as_view()), name='filebrowser'),

    #########################################################
    # History URLs.
    # TODO: Non-DRY. Break out into something like
    # ('/_history/',
    #  include(history_urls(list_view=..,compare_view=..)))?
    #########################################################
    url(r'^(?P<slug>.+)/_history/compare/$',
        slugify(PageCompareView.as_view())),
    url((r'^(?P<slug>.+)/_history/'
            r'(?P<version1>[0-9]+)\.\.\.(?P<version2>[0-9]+)?$'),
        slugify(PageCompareView.as_view()), name='compare-revisions'),
    url(r'^(?P<slug>.+)/_history/(?P<date1>%s)\.\.\.(?P<date2>%s)?$'
        % (DATETIME_REGEXP, DATETIME_REGEXP),
        slugify(PageCompareView.as_view()), name='compare-dates'),
    url(r'^(?P<slug>.+)/_history/(?P<version>[0-9]+)$',
        slugify(PageVersionDetailView.as_view()), name='as_of_version'),
    url(r'^(?P<slug>.+)/_history/(?P<date>%s)$' % DATETIME_REGEXP,
        slugify(PageVersionDetailView.as_view()), name='as_of_date'),
    url(r'^(?P<slug>.+)/_history/_feed/*$', PageChangesFeed(),
        name='changes-feed'),
    url(r'^(?P<slug>.+)/_history/$', slugify(PageVersionsList.as_view()),
        name='history'),

    ##########################################################
    # Basic edit actions.
    ##########################################################
    url(r'^(?P<slug>.+)/_edit$', slugify(PageUpdateView.as_view()),
        name='edit'),
    url(r'^(?P<slug>.+)/_delete$', slugify(PageDeleteView.as_view()),
        name='delete'),
    url(r'^(?P<slug>.+)/_revert/(?P<version>[0-9]+)$',
        slugify(PageRevertView.as_view()), name='revert'),

    url(r'^_create$', PageCreateView.as_view(), name='create'),

    url(r'^(?P<slug>.+)/_rename$', PageRenameView.as_view(), name='rename'),

    # TODO: Break this out, use tastypie or something similar
    ##########################################################
    # API
    ##########################################################
    url(r'^api/pages/suggest', suggest),

    ##########################################################
    # Basic page URLs.
    ##########################################################
    url(r'^/*$', slugify(PageDetailView.as_view()),
        kwargs={'slug': 'Front Page'}, name='frontpage'),
    url(r'^(?i)All_Pages/*$', ListView.as_view(**page_list_info),
        name='index'),
    # Catch-all and route to a page.
    url(r'^(?P<slug>.+?)/*$', slugify(PageDetailView.as_view()),
        name='show'),
)
