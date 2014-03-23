from haystack import indexes
from celery_haystack.indexes import CelerySearchIndex

from .models import Region


class RegionIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    slug = indexes.CharField(model_attr='slug', boost=2.5)
    full_name = indexes.CharField(model_attr='full_name', boost=2.5)
    # We add this for autocomplete.
    name_auto = indexes.EdgeNgramField(model_attr='full_name')
    slug_auto = indexes.EdgeNgramField(model_attr='slug')

    def get_model(self):
        return Region
