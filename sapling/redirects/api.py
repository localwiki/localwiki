from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from models import Redirect
from pages.api import PageResource, PageHistoryResource
from sapling.api import api


class RedirectResource(ModelResource):
    destination = fields.ForeignKey(PageResource, 'destination')

    class Meta:
        queryset = Redirect.objects.all()
        detail_uri_name = 'source'
        filtering = {
            'destination': ALL_WITH_RELATIONS,
            'source': ALL,
        }


# We don't use the SlugifyMixin approach here because it becomes
# too complicated to generate pretty URLs with the historical version
# identifiers.
class RedirectHistoryResource(ModelResource):
    destination = fields.ForeignKey(PageHistoryResource, 'destination')

    class Meta:
        resource_name = 'redirect_version'
        queryset = Redirect.versions.all()
        filtering = {
            'destination': ALL,
            'source': ALL,
        }

api.register(RedirectResource())
api.register(RedirectHistoryResource())
