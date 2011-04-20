from django.views.decorators.http import require_POST
from django.views.generic.simple import direct_to_template
from django.views.generic import DetailView, ListView
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from ckeditor.views import ck_upload_result
from versionutils import diff
from utils.views import Custom404Mixin, CreateObjectMixin
from utils.views import UpdateView, DeleteView, RevertView, HistoryView
from models import Page, PageImage, url_to_name
from forms import PageForm

# Where possible, we subclass similar generic views here.


class PageDetailView(Custom404Mixin, DetailView):
    model = Page
    context_object_name = 'page'

    def handler404(self, request, *args, **kwargs):
        return HttpResponseNotFound(
            direct_to_template(request, 'pages/page_new.html',
                               {'name': url_to_name(kwargs['original_slug']),
                                'page': Page(slug=kwargs['slug'])})
        )

    def get_context_data(self, **kwargs):
        context = super(PageDetailView, self).get_context_data(**kwargs)
        context['date'] = self.object.history.most_recent().history_info.date
        return context


class PageVersionDetailView(PageDetailView):
    template_name = 'pages/page_detail.html'

    def get_object(self):
        page = Page(slug=self.kwargs['slug'])
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

    def success_msg(self):
        # NOTE: This is eventually marked as safe when rendered in our
        # template.  So do *not* allow unescaped user input!
        map_create_link = ''
        if not hasattr(self.object, 'mapdata'):
            slug = self.object.pretty_slug
            map_create_link = (
                '<p><a href="%s">[map icon] Create a map for this page?'
                '</a></p>' % reverse('edit-mapdata', args=[slug])
            )
        return (
            '<div>Thank you for your changes. '
            'Your attention to detail is appreciated.</div>'
            '%s' % map_create_link
        )

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

    def get_object(self):
        page = Page(slug=self.kwargs['slug'])
        return page.history.as_of(version=int(self.kwargs['version']))

    def get_success_url(self):
        # Redirect back to the page.
        return reverse('show-page', args=[self.kwargs.get('original_slug')])


class PageHistoryView(HistoryView):
    def get_queryset(self):
        all_page_history = Page(slug=self.kwargs['slug']).history.all()
        # We set self.page to the most recent historical instance of the
        # page.
        self.page = all_page_history[0]
        return all_page_history

    def get_context_data(self, **kwargs):
        context = super(PageHistoryView, self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class PageFilesView(ListView):
    context_object_name = "file_list"
    template_name = "pages/page_files.html"

    def get_queryset(self):
        return PageImage.objects.filter(slug__exact=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(PageFilesView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['original_slug']
        return context


class PageCompareView(diff.views.CompareView):
    model = Page

    def get_object(self):
        return Page(slug=self.kwargs['slug'])


@require_POST
def upload(request, slug, **kwargs):
    uploaded = request.FILES['upload']
    try:
        image = PageImage(file=uploaded, name=uploaded.name, slug=slug)
        image.save()
        return ck_upload_result(request, url=image.file.url)
    except IntegrityError:
        return ck_upload_result(request,
                                message='A file with this name already exists')
