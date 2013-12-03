from rest_framework import serializers

from .models import PageFile


class HyperlinkedFileField(serializers.FileField):
    """
    Link to the full file URI rather than provide a relative path.
    """
    def to_native(self, value):
        request = self.context.get('request', None)
        return request.build_absolute_uri(value.url) 


class FileSerializer(serializers.HyperlinkedModelSerializer):
    file = HyperlinkedFileField()

    class Meta:
        model = PageFile
        fields = ('url', 'name', 'file', 'slug', 'region')
