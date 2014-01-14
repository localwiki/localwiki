from rest_framework import serializers
from rest_framework.exceptions import ParseError

from localwiki.main.api.fields import HISTORY_FIELDS

from .models import Tag, PageTagSet


class TagSetSerializer(serializers.Field):
    def to_native(self, obj):
        return [tag.slug for tag in obj.all()]



class HistoricalPageTagSetSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.RelatedField(source='tags', many=True)

    class Meta:
        model = PageTagSet.versions.model
        fields = ('url', 'page', 'region', 'tags') + HISTORY_FIELDS
