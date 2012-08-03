from tastypie.resources import ModelResource
from tastypie import fields

from users.api import UserResource


class ModelHistoryResource(ModelResource):
    history_user = fields.ForeignKey(UserResource, 'history_user', null=True)
