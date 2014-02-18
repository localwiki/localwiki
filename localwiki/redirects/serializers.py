from rest_framework import serializers

from localwiki.main.api.fields import HISTORY_FIELDS

from .models import Redirect


class RedirectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Redirect
        fields = ('url', 'source', 'destination', 'region')


class HistoricalRedirectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Redirect.versions.model
        fields = ('url', 'source', 'destination', 'region') + HISTORY_FIELDS
