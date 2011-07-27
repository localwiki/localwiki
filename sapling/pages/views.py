from dateutil.parser import parse as dateparser
import copy

from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.generic.base import RedirectView
from django.views.generic.simple import direct_to_template
from django.views.generic import DetailView, ListView
from django.http import (HttpResponseNotFound, HttpResponseRedirect,
                         HttpResponseBadRequest)
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from ckeditor.views import ck_upload_result
from versionutils import diff
from versionutils.versioning.views import UpdateView, DeleteView
from versionutils.versioning.views import RevertView, HistoryList
from utils.views import Custom404Mixin, CreateObjectMixin
from models import Page, PageFile, url_to_name
from forms import PageForm, PageFileForm
from maps.widgets import InfoMap

# Where possible, we subclass similar generic views here.


class PageDetailView(Custom404Mixin, DetailView):
    model = Page
    context_object_name = 'page'

    def handler404(self, request, *args, **kwargs):
        name = url_to_name(kwargs['original_slug'])
        return HttpResponseNotFound(
            direct_to_template(request, 'pages/page_new.html',
                               {'page': Page(name=name, slug=kwargs['slug'])})
        )

    def get_context_data(self, **kwargs):
        context = super(PageDetailView, self).get_context_data(**kwargs)
        context['date'] = self.object.history.most_recent().history_info.date
        if hasattr(self.object, 'mapdata'):
            # Remove the PanZoomBar on normal page views.
            olwidget_options = copy.deepcopy(getattr(settings,
                'OLWIDGET_DEFAULT_OPTIONS', {}))
            map_opts = olwidget_options.get('map_options', {})
            map_controls = map_opts.get('controls', [])
            if 'PanZoomBar' in map_controls:
                map_controls.remove('PanZoomBar')
            olwidget_options['map_options'] = map_opts
            olwidget_options['map_div_class'] = 'mapwidget small'
            context['map'] = InfoMap(
                [(self.object.mapdata.geom, self.object.name)],
                options=olwidget_options)
        return context


class PageVersionDetailView(PageDetailView):
    template_name = 'pages/page_detail.html'

    def get_object(self):
        page = Page(slug=self.kwargs['slug'])
        version = self.kwargs.get('version')
        date = self.kwargs.get('date')
        if version:
            return page.history.as_of(version=int(version))
        if date:
            return page.history.as_of(date=dateparser(date))

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
                '<p class="create_map"><a href="%s">'
                'Create a map for this page?'
                '</a></p>' % reverse('maps:edit', args=[slug])
            )
        return (
            '<div>Thank you for your changes. '
            'Your attention to detail is appreciated.</div>'
            '%s' % map_create_link
        )

    def get_success_url(self):
        return reverse('pages:show', args=[self.object.pretty_slug])

    def create_object(self):
        return Page(name=url_to_name(self.kwargs['original_slug']))


class PageDeleteView(DeleteView):
    model = Page
    context_object_name = 'page'

    def get_success_url(self):
        # Redirect back to the page.
        return reverse('pages:show', args=[self.kwargs.get('original_slug')])


class PageRevertView(RevertView):
    model = Page
    context_object_name = 'page'

    def get_object(self):
        page = Page(slug=self.kwargs['slug'])
        return page.history.as_of(version=int(self.kwargs['version']))

    def get_success_url(self):
        # Redirect back to the page.
        return reverse('pages:show', args=[self.kwargs.get('original_slug')])


class PageHistoryList(HistoryList):
    def get_queryset(self):
        all_page_history = Page(slug=self.kwargs['slug']).history.all()
        # We set self.page to the most recent historical instance of the
        # page.
        if all_page_history:
            self.page = all_page_history[0]
        else:
            self.page = Page(slug=self.kwargs['slug'],
                             name=self.kwargs['original_slug'])
        return all_page_history

    def get_context_data(self, **kwargs):
        context = super(PageHistoryList, self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class PageFileListView(ListView):
    context_object_name = "file_list"
    template_name = "pages/page_files.html"

    def get_queryset(self):
        return PageFile.objects.filter(slug__exact=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(PageFileListView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['original_slug']
        return context


class PageFilebrowserView(PageFileListView):
    template_name = 'pages/cke_filebrowser.html'

    def get_context_data(self, **kwargs):
        context = super(PageFilebrowserView, self).get_context_data(**kwargs)
        filter = self.kwargs.get('filter', 'files')
        if filter == 'images':
            self.object_list = [f for f in self.object_list if f.is_image()]
            context['thumbnail'] = True
        return context


class PageFileView(RedirectView):
    permanent = False

    def get_redirect_url(self, slug, file, **kwargs):
        page_file = get_object_or_404(PageFile, slug__exact=slug,
                                      name__exact=file)
        return page_file.file.url


class PageFileVersionDetailView(RedirectView):

    def get_redirect_url(self, slug, file, **kwargs):
        page_file = PageFile(slug=slug, name=file)
        version = self.kwargs.get('version')
        date = self.kwargs.get('date')

        if version:
            page_file = page_file.history.as_of(version=int(version))
        if date:
            page_file = page_file.history.as_of(date=dateparser(date))

        return page_file.file.url


class PageFileCompareView(diff.views.CompareView):
    model = PageFile

    def get_object(self):
        return PageFile(slug=self.kwargs['slug'], name=self.kwargs['file'])

    def get_context_data(self, **kwargs):
        context = super(PageFileCompareView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['original_slug']
        return context


class PageFileRevertView(RevertView):
    model = PageFile
    context_object_name = 'file'

    def get_object(self):
        file = PageFile(slug=self.kwargs['slug'], name=self.kwargs['file'])
        return file.history.as_of(version=int(self.kwargs['version']))

    def get_success_url(self):
        # Redirect back to the file info page.
        return reverse('pages:file-info', args=[self.kwargs['slug'],
                                                self.kwargs['file']])


class PageFileInfo(HistoryList):
    template_name_suffix = '_info'

    def get_queryset(self):
        all_file_history = PageFile(slug=self.kwargs['slug'],
                                    name=self.kwargs['file']).history.all()
        # We set self.file to the most recent historical instance of the
        # file.
        if all_file_history:
            self.file = all_file_history[0]
        else:
            self.file = PageFile(slug=self.kwargs['slug'],
                                 name=self.kwargs['file'])
        return all_file_history

    def get_context_data(self, **kwargs):
        context = super(PageFileInfo, self).get_context_data(**kwargs)
        context['file'] = self.file
        context['form'] = PageFileForm()
        return context


class PageCompareView(diff.views.CompareView):
    model = Page

    def get_object(self):
        return Page(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(PageCompareView, self).get_context_data(**kwargs)
        context['page_diff'] = diff.diff(context['old'], context['new'])
        return context


@require_POST
def upload(request, slug, **kwargs):
    error = None
    file_form = PageFileForm(request.POST, request.FILES)

    uploaded = request.FILES['file']
    if 'file' in kwargs:
        # Replace existing file if exists
        try:
            file = PageFile.objects.get(slug__exact=slug,
                                        name__exact=kwargs['file'])
            file.file = uploaded
        except PageFile.DoesNotExist:
            file = PageFile(file=uploaded, name=uploaded.name, slug=slug)
        file_form.instance = file
        if not file_form.is_valid():
            error = file_form.errors.values()[0]
        else:
            file_form.save()

        if error is not None:
            return HttpResponseBadRequest(error)
        return HttpResponseRedirect(reverse('pages:file-info',
                                            args=[slug, kwargs['file']]))

    # uploaded from ckeditor
    relative_url = '_files/' + uploaded.name
    try:
        file = PageFile(file=uploaded, name=uploaded.name, slug=slug)
        file.save()
        return ck_upload_result(request, url=relative_url)
    except IntegrityError:
        error = 'A file with this name already exists'
    return ck_upload_result(request, url=relative_url, message=error)
