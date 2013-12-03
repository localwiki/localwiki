from rest_framework import viewsets

from main.api import router

from .models import Page, PageFile
from .serializers import PageSerializer, FileSerializer


class PageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows pages to be viewed and edited.
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer

    def post_save(self, page, *args, **kwargs):
        if not hasattr(page, 'tags'):
            # Not providing any tag detail, so let's skip altering the tags.
            return

        if type(page.tags) is list:
            # If tags were provided in the request
            import pdb;pdb.set_trace()


class FileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows files to be viewed and edited.
    """
    queryset = PageFile.objects.all()
    serializer_class = FileSerializer


router.register(u'pages', PageViewSet)
router.register(u'files', FileViewSet)
