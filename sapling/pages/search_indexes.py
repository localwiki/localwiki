from haystack.indexes import *
from haystack import site

from models import Page


class PageIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    # TODO: We'll likely need to tweak this boost value.
    name = CharField(model_attr='name', boost=2)


site.register(Page, PageIndex)
