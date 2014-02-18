from rest_framework.permissions import DjangoObjectPermissions


class DjangoObjectPermissionsOrAnonReadOnly(DjangoObjectPermissions):
   authenticated_users_only = False
