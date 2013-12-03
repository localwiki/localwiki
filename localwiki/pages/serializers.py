from rest_framework import serializers

from .models import Page, PageFile


class HyperlinkedFileField(serializers.FileField):
    """
    Link to the full file URI rather than provide a relative path.
    """
    def to_native(self, value):
        request = self.context.get('request', None)
        return request.build_absolute_uri(value.url) 


class PageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page
        fields = ('url', 'name', 'slug', 'content', 'region')


class FileSerializer(serializers.HyperlinkedModelSerializer):
    file = HyperlinkedFileField()

    class Meta:
        model = PageFile
        fields = ('url', 'name', 'file', 'slug', 'region')
