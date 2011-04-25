from haystack.indexes import *
from haystack import site

from models import Page


class PageIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)


site.register(Page, PageIndex)
