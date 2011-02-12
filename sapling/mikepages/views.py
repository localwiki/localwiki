from models import Page
from forms import PageForm
from django.views.generic.simple import direct_to_template
from django.views.generic import DetailView, UpdateView
from ckeditor.views import ck_upload

from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
from utils.views import Custom404Mixin, CreateObjectMixin

class PageDetailView(Custom404Mixin, DetailView):
    model = Page
    context_object_name = 'page'
    
    def handler404(self, request, slug): 
        return HttpResponseNotFound(direct_to_template(request, 'mikepages/page_new.html', {'name': slug}))
    

class PageUpdateView(CreateObjectMixin, UpdateView):
    model = Page
    form_class = PageForm
    
    def get_success_url(self):
        return reverse('show-page', args=[self.object.slug])
    
    def create_object(self):
        return Page(name=self.kwargs['slug']) 
    

def upload(request, slug):
    return ck_upload(request, 'ck_upload/')