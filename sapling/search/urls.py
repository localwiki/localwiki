from django.conf.urls.defaults import *

from haystack.views import SearchView
from haystack.forms import SearchForm as DefaultSearchForm


class SearchForm(DefaultSearchForm):
    def search(self):
        sqs = super(SearchForm, self).search()
        cleaned_data = getattr(self, 'cleaned_data', None)
        if cleaned_data:
            return sqs.filter_or(name=cleaned_data['q'])
        return sqs


urlpatterns = patterns('',
    url(r'^$', SearchView(form_class=SearchForm), name='haystack_search'),
)
