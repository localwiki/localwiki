from django.contrib.auth.models import User, Group

from rest_framework import viewsets

from main.api import router

from .serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


router.register(r'users', UserViewSet)
