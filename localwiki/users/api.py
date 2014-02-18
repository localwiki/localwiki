from django.contrib.auth.models import User, Group

from rest_framework import viewsets
from rest_framework_filters import filters, FilterSet

from main.api import router
from main.api.views import AllowFieldLimitingMixin

from .serializers import UserSerializer

DATETIME_INPUT_FORMATS = (
    '%Y-%m-%dT%H:%M:%S.%f',
)

class UserFilter(FilterSet):
    date_joined = filters.AllLookupsFilter(name='date_joined')
    username = filters.AllLookupsFilter(name='username')

    class Meta:
        model = User
        fields = ('date_joined', 'username', 'first_name', 'last_name')


class UserViewSet(AllowFieldLimitingMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.

    Filter fields
    -------------

    You can filter the result set by providing the following query parameters:

      * `username` -- Filter by username. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups)
      * `first_name` -- Filter by first name, exact match.
      * `last_name` -- Filter by last name, exact match.
      * `date_joined` -- Filter by date joined. Supports the [standard lookup types](http://localwiki.net/main/API_Documentation#lookups).

    Ordering
    --------

    You can order the result set by providing the `ordering` query parameter with the value of one of:

      * `username`
      * `date_joined`

    You can reverse ordering by using the `-` sign, e.g. `-username`.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_class = UserFilter
    ordering_fields = ('username', 'date_joined')


router.register(r'users', UserViewSet)
