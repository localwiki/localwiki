from dateutil.parser import parse as dateparser
import time
import copy

from django.conf import settings
from django.views.generic.base import RedirectView
from django.views.generic import (DetailView, ListView,
    FormView)
from django.http import (HttpResponseNotFound, HttpResponseRedirect,
                         HttpResponseBadRequest, HttpResponse)
from django import forms
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render
from django.utils.html import escape
from django.utils.http import urlquote
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from ckeditor.views import ck_upload_result
from versionutils import diff
from versionutils.versioning.views import UpdateView, DeleteView
from versionutils.versioning.views import RevertView, VersionsList
from localwiki.utils.views import (Custom404Mixin, CreateObjectMixin,
    PermissionRequiredMixin)
from regions.models import Region
from regions.views import RegionMixin
from models import Page, PageFile, url_to_name
from forms import PageForm, PageFileForm
from maps.widgets import InfoMap

from models import slugify, clean_name
from utils import is_user_page
from exceptions import PageExistsError
from users.decorators import permission_required

# Where possible, we subclass similar generic views here.


class PageListView(RegionMixin, ListView):
    model = Page
    context_object_name = 'page_list'

    def get_queryset(self):
        qs = super(PageListView, self).get_queryset()
        return qs.defer('content').order_by('name')


class PageDetailView(Custom404Mixin, RegionMixin, DetailView):
    model = Page
    context_object_name = 'page'

    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Page,
            slug=slugify(slug), region=self.get_region())

    def handler404(self, request, *args, **kwargs):
        name = url_to_name(kwargs['original_slug'])
        region = Region.objects.get(slug=kwargs['region'])
        slug = kwargs['slug']

        page_templates = Page.objects.filter(
                slug__startswith='templates/', region=region
            ).order_by('name')
        page = Page(name=name, slug=slug, region=region)
        return HttpResponseNotFound(
            render(request, 'pages/page_new.html',
                   {'page': page, 'page_templates': page_templates,
                    'region': region})
        )

    def get_context_data(self, **kwargs):
        context = super(PageDetailView, self).get_context_data(**kwargs)
        context['region'] = self.object.region
        context['date'] = self.object.versions.most_recent().version_info.date
        if hasattr(self.object, 'mapdata'):
            # Remove the PanZoom on normal page views.
            olwidget_options = copy.deepcopy(getattr(settings,
                'OLWIDGET_DEFAULT_OPTIONS', {}))
            map_opts = olwidget_options.get('map_options', {})
            map_controls = map_opts.get('controls', [])
            if 'PanZoom' in map_controls:
                map_controls.remove('PanZoom')
            if 'PanZoomBar' in map_controls:
                map_controls.remove('PanZoomBar')
            if 'KeyboardDefaults' in map_controls:
                map_controls.remove('KeyboardDefaults')
            olwidget_options['map_options'] = map_opts
            olwidget_options['map_div_class'] = 'mapwidget small'
            context['map'] = InfoMap(
                [(self.object.mapdata.geom, self.object.name)],
                options=olwidget_options)
        return context


class PageVersionDetailView(PageDetailView):
    template_name = 'pages/page_version_detail.html'

    def get_object(self):
        page = Page(slug=self.kwargs['slug'], region=self.get_region())
        version = self.kwargs.get('version')
        date = self.kwargs.get('date')
        if version:
            return page.versions.as_of(version=int(version))
        if date:
            return page.versions.as_of(date=dateparser(date))

    def get_context_data(self, **kwargs):
        # we don't want PageDetailView's context, skip to DetailView's
        context = super(DetailView, self).get_context_data(**kwargs)
        context['region'] = self.get_region()
        context['date'] = self.object.version_info.date
        context['show_revision'] = True
        return context


class PageUpdateView(PermissionRequiredMixin, CreateObjectMixin,
                     RegionMixin, UpdateView):
    model = Page
    form_class = PageForm
    permission = 'pages.change_page'

    def success_msg(self):
        # NOTE: This is eventually marked as safe when rendered in our
        # template.  So do *not* allow unescaped user input!
        message = _('Thank you for your changes. '
                   'Your attention to detail is appreciated.')
        if not self.request.user.is_authenticated():
            message = (_('Changes saved! To use your name when editing, please '
                '<a href="%(login_url)s?next=%(current_path)s"><strong>log in</strong></a> or '
                '<a href="%(register_url)s?next=%(current_path)s"><strong>create an account</strong></a>.')
                % {'login_url': reverse('django.contrib.auth.views.login'),
                   'current_path' :self.request.path,
                   'register_url': reverse('registration_register')
                   }
                )
        map_create_link = ''
        if not hasattr(self.object, 'mapdata') and not is_user_page(self.object):
            slug = self.object.pretty_slug
            map_create_link = (_(
                '<p class="create_map"><a href="%s" class="button little map">'
                '<span class="text">Create a map</span></a> '
                'for this page?</p>') %
                reverse('maps:edit', args=[self.object.region.slug, slug])
            )
        return '<div>%s</div>%s' % (message, map_create_link)

    def get_success_url(self):
        return reverse('pages:show',
            args=[self.kwargs['region'], self.object.pretty_slug])

    def create_object(self):
        pagename = clean_name(self.kwargs['original_slug'])
        content = _('<p>Describe %s here</p>') % pagename
        if 'template' in self.request.GET:
            try:
                p = Page.objects.get(
                        slug=self.request.GET['template'],
                        region=self.get_region())
                content = p.content
            except Page.DoesNotExist:
                pass
        return Page(name=url_to_name(self.kwargs['original_slug']),
                    content=content, region=self.get_region())


class PageDeleteView(PermissionRequiredMixin, DeleteView):
    model = Page
    context_object_name = 'page'
    permission = 'pages.delete_page'

    def get_success_url(self):
        # Redirect back to the page.
        return reverse('pages:show',
            args=[self.kwargs.get('region'), self.kwargs.get('original_slug')])


class PageRevertView(PermissionRequiredMixin, RegionMixin, RevertView):
    model = Page
    context_object_name = 'page'
    permission = 'pages.delete_page'

    def get_object(self):
        page = Page(slug=self.kwargs['slug'], region=self.get_region())
        return page.versions.as_of(version=int(self.kwargs['version']))

    def get_success_url(self):
        # Redirect back to the page.
        return reverse('pages:show',
            args=[self.kwargs.get('region'), self.kwargs.get('original_slug')])


class PageVersionsList(RegionMixin, VersionsList):
    def get_queryset(self):
        p = Page(slug=self.kwargs['slug'], region=self.get_region())
        all_page_versions = p.versions.all()
        # We set self.page to the most recent historical instance of the
        # page.
        if all_page_versions:
            self.page = all_page_versions[0]
        else:
            self.page = Page(slug=self.kwargs['slug'],
                             name=self.kwargs['original_slug'],
                             region=self.get_region())
        return all_page_versions

    def get_context_data(self, **kwargs):
        context = super(PageVersionsList, self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class PageFileListView(RegionMixin, ListView):
    context_object_name = "file_list"
    template_name = "pages/page_files.html"

    def get_queryset(self):
        return PageFile.objects.filter(
            slug__exact=self.kwargs['slug'], region=self.get_region())

    def get_context_data(self, **kwargs):
        context = super(PageFileListView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['original_slug']
        context['region'] = self.get_region()
        return context


class PageFilebrowserView(PageFileListView):
    template_name = 'pages/cke_filebrowser.html'

    def get_context_data(self, **kwargs):
        context = super(PageFilebrowserView, self).get_context_data(**kwargs)
        _filter = self.kwargs.get('filter', 'files')
        if _filter == 'images':
            self.object_list = [f for f in self.object_list if f.is_image()]
            context['thumbnail'] = True
        return context


class PageFileView(RegionMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, slug, file, **kwargs):
        page_file = get_object_or_404(PageFile,
            slug__exact=slug, name__exact=file, region=self.get_region())
        return page_file.file.url


class PageFileVersionDetailView(RegionMixin, RedirectView):
    def get_redirect_url(self, slug, file, **kwargs):
        page_file = PageFile(slug=slug, name=file, region=self.get_region())
        version = self.kwargs.get('version')
        date = self.kwargs.get('date')

        if version:
            page_file = page_file.versions.as_of(version=int(version))
        if date:
            page_file = page_file.versions.as_of(date=dateparser(date))

        return page_file.file.url


class PageFileCompareView(RegionMixin, diff.views.CompareView):
    model = PageFile

    def get_object(self):
        return PageFile(
            slug=self.kwargs['slug'],
            name=self.kwargs['file'],
            region=self.get_region())

    def get_context_data(self, **kwargs):
        context = super(PageFileCompareView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['original_slug']
        context['region'] = self.kwargs['region']
        return context


class PageFileRevertView(PermissionRequiredMixin, RegionMixin, RevertView):
    model = PageFile
    context_object_name = 'file'
    permission = 'pages.change_page'

    def get_object(self):
        _file = PageFile(slug=self.kwargs['slug'],
                        name=self.kwargs['file'],
                        region=self.get_region())
        return _file.versions.as_of(version=int(self.kwargs['version']))

    def get_protected_object(self):
        return Page.objects.get(slug=self.object.slug, region=self.get_region())

    def get_success_url(self):
        # Redirect back to the file info page.
        return reverse('pages:file-info', args=[self.kwargs['region'],
                                                self.kwargs['slug'],
                                                self.kwargs['file']])


class PageFileInfo(RegionMixin, VersionsList):
    template_name_suffix = '_info'

    def get_queryset(self):
        all_file_versions = PageFile(
            slug=self.kwargs['slug'],
            name=self.kwargs['file'],
            region=self.get_region()
        ).versions.all()
        # We set self.file to the most recent historical instance of the
        # file.
        if all_file_versions:
            self.file = all_file_versions[0]
        else:
            self.file = PageFile(slug=self.kwargs['slug'],
                                 name=self.kwargs['file'],
                                 region=self.get_region())
        return all_file_versions

    def get_context_data(self, **kwargs):
        context = super(PageFileInfo, self).get_context_data(**kwargs)
        context['file'] = self.file
        context['form'] = PageFileForm()
        return context


class PageCompareView(RegionMixin, diff.views.CompareView):
    model = Page

    def get_object(self):
        return Page(slug=self.kwargs['slug'], region=self.get_region())

    def get_context_data(self, **kwargs):
        context = super(PageCompareView, self).get_context_data(**kwargs)
        context['page_diff'] = diff.diff(context['old'], context['new'])
        return context


class PageCreateView(RegionMixin, RedirectView):
    """
    A convenience view that redirects either to the editor (for a new
    page) or to the page (if it already exists).
    """
    def get_redirect_url(self, **kwargs):
        pagename = self.request.GET.get('pagename')
        if not pagename.strip():
            # No page name provided, so let's return a useful error message.
            messages.add_message(self.request, messages.SUCCESS,
                _('You must provide a page name when creating a page.'))
            return reverse('haystack_search')

        slug = slugify(pagename)
        region = self.get_region()
        if Page.objects.filter(slug=slug, region=region).exists():
            return Page.objects.get(slug=slug, region=region).get_absolute_url()
        else:
            return reverse('pages:edit', args=[self.kwargs['region'], pagename])


def _find_available_filename(filename, slug, region):
    """
    Returns a filename that isn't taken for the given page slug.
    """
    basename, ext = filename.rsplit(".", 1)
    suffix_count = 1
    while PageFile.objects.filter(name=filename, slug=slug,
                                  region=region).exists():
        suffix_count += 1
        filename = "%s %d.%s" % (basename, suffix_count, ext)
    return filename


@permission_required('pages.change_page',
    (Page, 'slug', 'slug', 'region__slug', 'region'))
def upload(request, **kwargs):
    # For GET, just return blank response. See issue #327.
    if request.method != 'POST':
        return HttpResponse('')
    error = None
    file_form = PageFileForm(request.POST, request.FILES)

    slug = kwargs['slug']
    region = Region.objects.get(slug=kwargs['region'])

    uploaded = request.FILES['file']
    if 'file' in kwargs:
        # Replace existing file if exists
        try:
            file = PageFile.objects.get(
                slug__exact=slug,
                name__exact=kwargs['file'],
                region=region
            )
            file.file = uploaded
        except PageFile.DoesNotExist:
            file = PageFile(
                file=uploaded,
                name=uploaded.name,
                slug=slug,
                region=region
            )
        file_form.instance = file
        if not file_form.is_valid():
            error = file_form.errors.values()[0]
        else:
            file_form.save()

        if error is not None:
            return HttpResponseBadRequest(error)
        return HttpResponseRedirect(
            reverse('pages:file-info',
                    args=[kwargs['region'], slug, kwargs['file']]))

    # uploaded from ckeditor
    filename = _find_available_filename(uploaded.name, slug, region)
    relative_url = '_files/' + urlquote(filename)
    try:
        file = PageFile(file=uploaded, name=filename, slug=slug, region=region)
        file.save()
        return ck_upload_result(request, url=relative_url)
    except IntegrityError:
        error = _('A file with this name already exists')
    return ck_upload_result(request, url=relative_url, message=error)


class RenameForm(forms.Form):
    pagename = forms.CharField(max_length=255, label=ugettext_lazy("Pagename"))
    comment = forms.CharField(max_length=150, required=False, label=ugettext_lazy("Comment"))


class PageRenameView(RegionMixin, FormView):
    form_class = RenameForm
    template_name = 'pages/page_rename.html'

    def form_valid(self, form):
        try:
            p = Page.objects.get(
                slug=slugify(self.kwargs['slug']),
                region=self.get_region()
            )
            self.new_pagename = form.cleaned_data['pagename']
            p.rename_to(self.new_pagename)
        except PageExistsError, s:
            messages.add_message(self.request, messages.SUCCESS, s)
            return HttpResponseRedirect(
                reverse('pages:show', args=[p.region.slug, p.slug]))

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(PageRenameView, self).get_context_data(**kwargs)
        context['page'] = Page.objects.get(slug=slugify(self.kwargs['slug']),
                                           region=self.get_region())
        return context

    def success_msg(self):
        # NOTE: This is eventually marked as safe when rendered in our
        # template.  So do *not* allow unescaped user input!
        return ('<div>' + _('Page renamed to "%s"') + '</div>') % escape(self.new_pagename)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS,
            self.success_msg())
        # Redirect back to the page.
        return reverse('pages:show',
            args=[self.kwargs['region'], self.new_pagename])


class PageRandomView(RegionMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        pgs_in_region = Page.objects.filter(region=self.get_region())
        return pgs_in_region.order_by('?')[0].get_absolute_url()


def suggest(request):
    """
    Simple page suggest.
    """
    # XXX TODO: Break this out when doing the API work.
    from haystack.query import SearchQuerySet 
    import json

    term = request.GET.get('term', None)
    if not term:
        return HttpResponse('')
    results = SearchQuerySet().autocomplete(name_auto=term) 
    results = [p.name for p in results]
    return HttpResponse(json.dumps(results))
