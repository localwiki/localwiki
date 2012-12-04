import copy
from dateutil.parser import parse as dateparser

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from versionutils.versioning.views import VersionsList, RevertView, UpdateView
from versionutils.diff.views import CompareView
from models import PageTagSet, Tag, slugify
from forms import PageTagSetForm
from pages.models import Page

from utils.views import CreateObjectMixin, PermissionRequiredMixin,\
    Custom404Mixin


class PageNotFoundMixin(Custom404Mixin):
    def handler404(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('pages:show',
                                            kwargs={'slug': kwargs['slug']}))


class TagListView(ListView):
    model = Tag

    def get_queryset(self):
        return super(TagListView, self).get_queryset().annotate(
                    num_pages=Count('pagetagset')).filter(num_pages__gt=0)


class TaggedList(ListView):
    model = PageTagSet

    def get_queryset(self):
        self.tag_name = slugify(self.kwargs['slug'])
        try:
            self.tag = Tag.objects.get(slug=self.tag_name)
            self.tag_name = self.tag.name
            return PageTagSet.objects.filter(tags=self.tag)
        except Tag.DoesNotExist:
            self.tag = None
            return PageTagSet.objects.none()

    def get_map_objects(self):
        if not self.tag:
            return None
        # We re-use the MapForTag view's logic here to embed a mini-map on the
        # tags list page
        from maps.views import MapForTag
        map_view = MapForTag()
        map_view.kwargs = dict(tag=self.tag.slug)
        map_view.object_list = map_view.get_queryset()
        return map_view.get_map_objects()

    def get_context_data(self, *args, **kwargs):
        from maps.widgets import InfoMap

        context = super(TaggedList, self).get_context_data(*args, **kwargs)
        context['tag'] = self.tag
        context['tag_name'] = self.tag_name
        map_objects = self.get_map_objects()
        if map_objects:
            # Remove the PanZoomBar on normal page views.
            olwidget_options = copy.deepcopy(getattr(settings,
                'OLWIDGET_DEFAULT_OPTIONS', {}))
            map_opts = olwidget_options.get('map_options', {})
            map_controls = map_opts.get('controls', [])
            if 'PanZoomBar' in map_controls:
                map_controls.remove('PanZoomBar')
            if 'KeyboardDefaults' in map_controls:
                map_controls.remove('KeyboardDefaults')
            olwidget_options['map_options'] = map_opts
            olwidget_options['map_div_class'] = 'mapwidget small'
            context['map'] = InfoMap(
                map_objects,
                options=olwidget_options)
        return context


class PageTagSetUpdateView(PageNotFoundMixin, PermissionRequiredMixin,
        CreateObjectMixin, UpdateView):
    model = PageTagSet
    form_class = PageTagSetForm
    permission = 'pages.change_page'

    def get_object(self):
        page_slug = self.kwargs.get('slug')
        page = get_object_or_404(Page, slug=page_slug)
        try:
            return PageTagSet.objects.get(page=page)
        except PageTagSet.DoesNotExist:
            return PageTagSet(page=page)

    def get_success_url(self):
        next = self.request.POST.get('next', None)
        if next:
            return next
        return reverse('pages:tags', args=[self.kwargs.get('slug')])

    def get_protected_object(self):
        return self.object.page


class PageTagSetVersions(PageNotFoundMixin, VersionsList):
    def get_queryset(self):
        page_slug = self.kwargs.get('slug')
        try:
            self.page = get_object_or_404(Page, slug=page_slug)
            return self.page.pagetagset.versions.all()
        except PageTagSet.DoesNotExist:
            return PageTagSet.versions.none()

    def get_context_data(self, **kwargs):
        context = super(PageTagSetVersions, self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class PageTagSetVersionDetailView(DetailView):
    context_object_name = 'pagetagset'
    template_name = 'tags/pagetagset_version_detail.html'

    def get_object(self):
        page_slug = self.kwargs.get('slug')
        try:
            page = Page.objects.get(slug=page_slug)
            tags = page.pagetagset
            version = self.kwargs.get('version')
            date = self.kwargs.get('date')
            if version:
                return tags.versions.as_of(version=int(version))
            if date:
                return tags.versions.as_of(date=dateparser(date))
        except (Page.DoesNotExist, PageTagSet.DoesNotExist):
            return None

    def get_context_data(self, **kwargs):
        context = super(PageTagSetVersionDetailView,
                        self).get_context_data(**kwargs)
        context['date'] = self.object.version_info.date
        context['show_revision'] = True
        return context


class PageTagSetCompareView(CompareView):
    model = PageTagSet

    def get_object(self):
        page_slug = self.kwargs.get('slug')
        page = Page.objects.get(slug=page_slug)
        return page.pagetagset

    def get_context_data(self, **kwargs):
        context = super(PageTagSetCompareView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['original_slug']
        return context


class PageTagSetRevertView(PermissionRequiredMixin, RevertView):
    model = PageTagSet
    context_object_name = 'pagetagset'
    permission = 'pages.change_page'

    def get_object(self):
        page_slug = self.kwargs.get('slug')
        page = Page.objects.get(slug=page_slug)
        return page.pagetagset.versions.as_of(
            version=int(self.kwargs['version']))

    def get_protected_object(self):
        return self.object.page

    def get_success_url(self):
        # Redirect back to the file info page.
        return reverse('pages:tags-history', args=[self.kwargs['slug']])


def suggest_tags(request):
    """
    Simple tag suggest.
    """
    # XXX TODO: Break this out when doing the API work.
    import json

    term = request.GET.get('term', None)
    if not term:
        return HttpResponse('')
    results = Tag.objects.filter(name__istartswith=term).exclude(
                                                            pagetagset=None)
    results = [t.name for t in results]
    return HttpResponse(json.dumps(results))
