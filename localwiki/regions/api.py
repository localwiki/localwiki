from rest_framework import viewsets

from main.api import router

from .models import Region
from .serializers import RegionSerializer


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows regions to be viewed.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


router.register(u'regions', RegionViewSet)
