from django.db import models
from pages.search_indexes import PageIndex
from tags.models import PageTagSet
from pages.models import Page


def reindex_page(sender, **kwargs):
    # Not sure if a way around the 'post_clear' here. We need to reindex
    # when the tag set is cleared because we have no way to know when
    # all the tags are deleted, otherwise.
    if kwargs['action'] in ['post_add', 'post_remove', 'post_clear']:
        PageIndex(Page).update_object(kwargs['instance'].page)

models.signals.m2m_changed.connect(reindex_page,
    sender=PageTagSet.tags.through)
