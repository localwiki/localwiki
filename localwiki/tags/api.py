from rest_framework import viewsets

from main.api import router

from .models import Tag, PageTagSet, slugify

from .serializers import HistoricalPageTagSetSerializer


class HistoricalTagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing tag history.
    """
    queryset = PageTagSet.versions.all()
    serializer_class = HistoricalPageTagSetSerializer


router.register(u'tags_history', HistoricalTagViewSet)
