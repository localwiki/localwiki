from rest_framework import viewsets

from main.api import router

from .models import Redirect
from .serializers import RedirectSerializer


class RedirectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows redirects to be viewed and edited.
    """
    queryset = Redirect.objects.all()
    serializer_class = RedirectSerializer


router.register(u'redirects', RedirectViewSet)
