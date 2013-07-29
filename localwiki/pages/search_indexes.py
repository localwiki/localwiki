from haystack.indexes import *
from haystack import site

from models import Page


class PageIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    # TODO: We'll likely need to tweak this boost value.
    name = CharField(model_attr='name', boost=2)
    # We add this for autocomplete.
    name_auto = EdgeNgramField(model_attr='name')
    tags = MultiValueField(boost=1.25)

    def prepare_tags(self, obj):
        from tags.models import PageTagSet
        try:
            return [tag.name  for tag in obj.pagetagset.tags.all()]
        except PageTagSet.DoesNotExist:
            return []


site.register(Page, PageIndex)
