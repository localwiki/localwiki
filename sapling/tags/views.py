from django.views.generic import UpdateView

from utils.views import CreateObjectMixin
from tags.models import PageTagSet, Tag
from tags.forms import PageTagSetForm
from pages.models import slugify, Page
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.http import HttpResponse


class TagListView(ListView):
    model = Tag


class TaggedList(ListView):
    model = PageTagSet

    def get_queryset(self):
        tag = Tag.objects.get(slug=self.kwargs['slug'])
        return PageTagSet.objects.filter(tags__in=[tag])


class PageTagSetUpdateView(CreateObjectMixin, UpdateView):
    model = PageTagSet
    form_class = PageTagSetForm
    template_name_suffix = '_info'

    def get_object(self):
        page_slug = self.kwargs.get('slug')
        page = Page.objects.get(slug=slugify(page_slug))
        try:
            return PageTagSet.objects.get(page=page)
        except PageTagSet.DoesNotExist:
            return PageTagSet(page=page)

    def get_success_url(self):
        next = self.request.POST.get('next', None)
        if next:
            return next
        return reverse('pages:tags', args=[self.kwargs.get('slug')])

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