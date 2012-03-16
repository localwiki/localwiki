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
        context['keywords'] = self.query.split()
        return context


class SearchForm(DefaultSearchForm):
    def search(self):
        sqs = super(SearchForm, self).search()
        cleaned_data = getattr(self, 'cleaned_data', {})
        keywords = cleaned_data.get('q', '').split()
        if not keywords:
            return sqs
        # we do __in because we want partial matches, not just exact ones
        return sqs.filter_or(name__in=keywords).filter_or(tags__in=keywords)

urlpatterns = patterns('',
    url(r'^$', CreatePageSearchView(form_class=SearchForm),
        name='haystack_search'),
)
