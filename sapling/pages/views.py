from django.views.generic.simple import direct_to_template
from django.views.generic import DetailView, UpdateView, ListView
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from ckeditor.views import ck_upload
from versionutils import diff
from utils.views import Custom404Mixin, CreateObjectMixin
from utils.views import DeleteView, RevertView, HistoryView
from models import Page, url_to_name
from forms import PageForm


# Where possible, we subclass similar generic views here.

class PageDetailView(Custom404Mixin, DetailView):
    model = Page
    context_object_name = 'page'

    def handler404(self, request, *args, **kwargs):
        return HttpResponseNotFound(
            direct_to_template(request, 'pages/page_new.html',
                               {'name': url_to_name(kwargs['original_slug'])})
        )

    def get_context_data(self, **kwargs):
        context = super(PageDetailView, self).get_context_data(**kwargs)
        context['date'] = self.object.history.most_recent().history_info.date
        return context


class PageVersionDetailView(PageDetailView):
    template_name = 'pages/page_detail.html'

    def get_object(self):
        page = super(PageVersionDetailView, self).get_object()
        return page.history.as_of(version=int(self.kwargs['version']))

    def get_context_data(self, **kwargs):
        # we don't want PageDetailView's context, skip to DetailView's
        context = super(DetailView, self).get_context_data(**kwargs)
        context['date'] = self.object.history_info.date
        context['show_revision'] = True
        return context


class PageUpdateView(CreateObjectMixin, UpdateView):
    model = Page
    form_class = PageForm

    def get_success_url(self):
        return reverse('show-page', args=[self.object.pretty_slug])

    def create_object(self):
        return Page(name=url_to_name(self.kwargs['original_slug']))


class PageDeleteView(DeleteView):
    model = Page
    context_object_name = 'page'

    def get_success_url(self):
        # Redirect back to the page.
        return reverse('show-page', args=[self.kwargs.get('original_slug')])


class PageRevertView(RevertView):
    model = Page
    context_object_name = 'page'

    def get_success_url(self):
        # Redirect back to the page.
        return reverse('show-page', args=[self.kwargs.get('original_slug')])


class PageHistoryView(HistoryView):
    def get_queryset(self):
        self.page = get_object_or_404(Page, slug__exact=self.kwargs['slug'])
        return self.page.history.all()

    def get_context_data(self, **kwargs):
        context = super(PageHistoryView, self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class PageCompareView(diff.views.CompareView):
    model = Page


def upload(request, slug, **kwargs):
    return ck_upload(request, 'ck_upload/')
