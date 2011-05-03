from django.conf.urls.defaults import *

from haystack.views import SearchView
from haystack.forms import SearchForm as DefaultSearchForm

from pages.models import Page, slugify


class CreatePageSearchView(SearchView):
    def extra_context(self):
        context = super(CreatePageSearchView, self).extra_context()
        context['page_exists_for_query'] = Page.objects.filter(
            slug=slugify(self.query))
        context['query_slug'] = Page(name=self.query).pretty_slug
        return context


class SearchForm(DefaultSearchForm):
    def search(self):
        sqs = super(SearchForm, self).search()
        cleaned_data = getattr(self, 'cleaned_data', None)
        if cleaned_data:
            return sqs.filter_or(name=cleaned_data['q'])
        return sqs

urlpatterns = patterns('',
    url(r'^$', CreatePageSearchView(form_class=SearchForm),
        name='haystack_search'),
)
