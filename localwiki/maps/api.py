from rest_framework import viewsets

from main.api import router

from .models import MapData
from .serializers import MapDataSerializer, HistoricalMapDataSerializer


class MapDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows maps to be viewed and edited.
    """
    queryset = MapData.objects.all()
    serializer_class = MapDataSerializer


class HistoricalMapDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows map history to be viewed.
    """
    queryset = MapData.versions.all()
    serializer_class = HistoricalMapDataSerializer


router.register(u'maps', MapDataViewSet)
router.register(u'maps_history', HistoricalMapDataViewSet)
