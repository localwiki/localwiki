from rest_framework_filters import filters, FilterSet

from users.api import UserFilter

class HistoricalFilter(FilterSet):
    history_date = filters.AllLookupsFilter(name='history_date')
    history_type = filters.AllLookupsFilter(name='history_type')
    history_user = filters.RelatedFilter(UserFilter, name='history_user')
    history_user_ip = filters.AllLookupsFilter(name='history_user_ip')
