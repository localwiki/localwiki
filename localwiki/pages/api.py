from rest_framework import viewsets

from main.api import router
from tags.models import Tag, PageTagSet, slugify

from .models import Page, PageFile
from .serializers import (PageSerializer, HistoricalPageSerializer,
    FileSerializer, HistoricalFileSerializer)

def get_or_create_tag(word, region):
    tag, created = Tag.objects.get_or_create(
        slug=slugify(word), region=region,
        defaults={'name': word}
    )
    return tag


class PageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows pages to be viewed and edited.

    Tags
    ---------------------

    Tags can be found in the `tags` attribute.  You can update
    *just* the tags by issuing a `PATCH` here with just the `tags`
    attribute present, e.g.:

        {"tags": ["park", "fun"]}

    To update a page and not change the tags, simply exclude the
    `tags` field from your update.

    To delete all tags from the page, issue a request with  `tags`
    set to `[]`.
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer

    def post_save(self, page, *args, **kwargs):
        if not hasattr(page, '_tags'):
            # Not providing any tag detail, so let's skip altering the tags.
            return

        if type(page._tags) is list:
            # If tags were provided in the request
            try:
                pts = PageTagSet.objects.get(page=page, region=page.region)
            except PageTagSet.DoesNotExist:
                pts = PageTagSet(page=page, region=page.region)
            pts.save()

            tags = []
            for word in page._tags:
                tags.append(get_or_create_tag(word, page.region))
            pts.tags = tags


class HistoricalPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing page history.
    """
    queryset = Page.versions.all()
    serializer_class = HistoricalPageSerializer


class FileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows files to be viewed and edited.
    """
    queryset = PageFile.objects.all()
    serializer_class = FileSerializer


class HistoricalFileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing file history.
    """
    queryset = PageFile.versions.all()
    serializer_class = HistoricalFileSerializer


router.register(u'pages', PageViewSet)
router.register(u'pages_history', HistoricalPageViewSet)
router.register(u'files', FileViewSet)
router.register(u'files_history', HistoricalFileViewSet)
