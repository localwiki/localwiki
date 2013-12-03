from rest_framework import viewsets

from main.api import router

from .models import PageFile
from .serializers import FileSerializer


class FileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows files to be viewed and edited.
    """
    queryset = PageFile.objects.all()
    serializer_class = FileSerializer


router.register(u'files', FileViewSet)
