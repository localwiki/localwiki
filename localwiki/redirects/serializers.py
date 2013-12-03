from rest_framework import serializers

from .models import Redirect


class RedirectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Redirect
        fields = ('url', 'source', 'destination', 'region')
