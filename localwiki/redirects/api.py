from rest_framework import viewsets

from main.api import router

from .models import Redirect
from .serializers import RedirectSerializer, HistoricalRedirectSerializer


class RedirectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows redirects to be viewed and edited.
    """
    queryset = Redirect.objects.all()
    serializer_class = RedirectSerializer


class HistoricalRedirectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows redirect history to be viewed.
    """
    queryset = Redirect.versions.all()
    serializer_class = HistoricalRedirectSerializer


router.register(u'redirects', RedirectViewSet)
router.register(u'redirects_history', HistoricalRedirectViewSet)
