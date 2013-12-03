from rest_framework import viewsets

from main.api import router

from .models import MapData
from .serializers import MapDataSerializer


class MapDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows maps to be viewed and edited.
    """
    queryset = MapData.objects.all()
    serializer_class = MapDataSerializer


router.register(u'maps', MapDataViewSet)
