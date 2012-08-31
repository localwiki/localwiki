from tastypie.resources import ModelResource, ALL

from django.contrib.auth.models import User
from sapling.api import api


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        fields = ['username', 'first_name', 'last_name', 'date_joined']
        filtering = {
            'username': ALL,
            'first_name': ALL,
            'last_name': ALL,
            'date_joined': ALL,
        }


api.register(UserResource())
