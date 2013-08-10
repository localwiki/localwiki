from tastypie.resources import ModelResource

from main.api import api

from regions.models import Region

class RegionResource(ModelResource):
    class Meta:
        queryset = Region.objects.all()


api.register(RegionResource())
