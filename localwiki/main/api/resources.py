from tastypie.resources import ModelResource
from tastypie import fields


class ModelHistoryResource(ModelResource):
    history_user = fields.ForeignKey('users.api.UserResource',
        'history_user', null=True)
