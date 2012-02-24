from dateutil.parser import parse as dateparser

from django.views.generic import UpdateView

from utils.views import CreateObjectMixin, PermissionRequiredMixin
from tags.models import PageTagSet, Tag
from tags.forms import PageTagSetForm
from pages.models import Page
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.http import HttpResponse
from versionutils.versioning.views import VersionsList, RevertView
from django.views.generic.detail import DetailView
from versionutils.diff.views import CompareView


class TagListView(ListView):
    model = Tag


class TaggedList(ListView):
    model = PageTagSet

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['slug'])
        return PageTagSet.objects.filter(tags__in=[self.tag])

    def get_context_data(self, *args, **kwargs):
        context = super(TaggedList, self).get_context_data(*args, **kwargs)
        context['tag'] = self.tag
        return context


class PageTagSetUpdateView(CreateObjectMixin, UpdateView):
    model = PageTagSet
    form_class = PageTagSetForm

    def get_object(self):
        page_slug = self.kwargs.get('slug')
        page = Page.objects.get(slug=page_slug)
        try:
            return PageTagSet.objects.get(page=page)
        except PageTagSet.DoesNotExist:
            return PageTagSet(page=page)

    def get_success_url(self):
        next = self.request.POST.get('next', None)
        if next:
            return next
        return reverse('pages:tags', args=[self.kwargs.get('slug')])


class PageTagSetVersions(VersionsList):
    def get_queryset(self):
        page_slug = self.kwargs.get('slug')
        try:
            self.page = Page.objects.get(slug=page_slug)
            return self.page.pagetagset.versions.all()
        except (Page.DoesNotExist, PageTagSet.DoesNotExist):
            pass
        return []

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
        return page.pagetagset.versions.as_of(version=int(
                                                    self.kwargs['version']))

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
    results = Tag.objects.filter(name__istartswith=term)
    results = [t.name for t in results]
    return HttpResponse(json.dumps(results))
