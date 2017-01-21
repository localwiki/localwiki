from haystack.indexes import *
from haystack import site

from models import Page
from tags.models import PageTagSet


class PageIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    # TODO: We'll likely need to tweak this boost value.
    name = CharField(model_attr='name', boost=2)
    tags = MultiValueField(boost=1.25)

    def prepare_tags(self, obj):
        try:
            return [tag.name  for tag in obj.pagetagset.tags.all()]
        except PageTagSet.DoesNotExist:
            return []


site.register(Page, PageIndex)
