from haystack import indexes
from celery_haystack.indexes import CelerySearchIndex

from models import Page


class PageIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    region_id = indexes.IntegerField(model_attr='region__id', null=True)
    # TODO: We'll likely need to tweak this boost value.
    name = indexes.CharField(model_attr='name', boost=2)
    # We add this for autocomplete.
    name_auto = indexes.EdgeNgramField(model_attr='name')
    tags = indexes.MultiValueField(boost=1.25)

    def get_model(self):
        return Page

    def prepare_tags(self, obj):
        from tags.models import PageTagSet
        try:
            return [tag.name  for tag in obj.pagetagset.tags.all()]
        except PageTagSet.DoesNotExist:
            return []
