from rest_framework import serializers
from rest_framework.exceptions import ParseError

from localwiki.main.api.fields import HISTORY_FIELDS
from tags.models import Tag, PageTagSet

from .models import Page, PageFile


class HyperlinkedFileField(serializers.FileField):
    """
    Link to the full file URI rather than provide a relative path.
    """
    def to_native(self, value):
        request = self.context.get('request', None)
        return request.build_absolute_uri(value.url) 


class TagSetSerializer(serializers.WritableField):
    def from_native(self, data):
        if type(data) is not list:
            raise ParseError("expected a list of data")    
        return {'tags': data}
     
    def to_native(self, obj):
        if type(obj) is list:
            return obj
        if not hasattr(obj, 'pagetagset'):
            return []
        return [tag.slug for tag in obj.pagetagset.tags.all()]


class PageSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagSetSerializer(source='*', required=False)

    class Meta:
        model = Page
        fields = ('url', 'name', 'slug', 'content', 'region', 'tags')

    def restore_object(self, attrs, instance=None):
        # 'tags' isn't an attribute of the Page model, so we have to
        # temporarily remove it here.
        tags = attrs.pop('tags', None)
        obj = super(PageSerializer, self).restore_object(attrs, instance)
        obj._tags = tags
        return obj

    def save(self, **kwargs):
        if self.partial and self.init_data.keys() == ['tags']:
            # Don't save the Page object if we're just saving tags.
            return self.object

        # Page renaming
        page = self.object
        old_page = None
        if page.id:
            old_page = Page.objects.get(id=page.id)
        if old_page and (page.name != old_page.name):
            return old_page.rename_to(page.name)

        return super(PageSerializer, self).save(**kwargs)


class HistoricalPageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page.versions.model
        fields = ('url', 'name', 'slug', 'content', 'region') + HISTORY_FIELDS


class FileSerializer(serializers.HyperlinkedModelSerializer):
    file = HyperlinkedFileField()

    class Meta:
        model = PageFile
        fields = ('url', 'name', 'file', 'slug', 'region')


class HistoricalFileSerializer(FileSerializer):
    class Meta:
        model = PageFile.versions.model
        fields = ('url', 'name', 'file', 'slug', 'region') + HISTORY_FIELDS
