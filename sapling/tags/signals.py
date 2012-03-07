from django.db import models
from pages.search_indexes import PageIndex
from tags.models import PageTagSet
from pages.models import Page

# Tags are part of a page's search index, so when PageTagSet is updated, we
# want to reindex the page.
def reindex_page(sender, **kwargs):
    PageIndex(Page).update_object(kwargs['instance'].page)
models.signals.post_save.connect(reindex_page, sender=PageTagSet)