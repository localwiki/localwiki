from django.shortcuts import render_to_response

from models import Page
from forms import PageForm
from django.views.generic.simple import direct_to_template
from django.template.defaultfilters import slugify
from ckeditor.views import ck_upload

from django.db.models import AutoField
from django.http import HttpResponse
def copy_model_instance(obj):
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and\
                       not f in obj._meta.parents.values()])
    return obj.__class__(**initial)

def diff(request):
    pages = Page.objects.all()
    page1 = pages[0]
    page2 = pages[1]
    return render_to_response('mikepages/page_diff.html', {'page1': page1, 'page2': page2})

def upload(request, slug):
    return ck_upload(request, 'ck_upload/')

def show(request, slug):
    try:
        page = Page.objects.get(slug__exact=slugify(slug))
    except Page.DoesNotExist:
        return direct_to_template(request, 'mikepages/page_new.html', {'name': slug})
    return direct_to_template(request, 'mikepages/page_detail.html', {'page': page})

def edit(request, slug):
    page_old = None
    try:
        page = Page.objects.get(slug__exact=slugify(slug))
        page_old = copy_model_instance(page)
    except Page.DoesNotExist:
        page = Page(name=slug)
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            if page_old:
                return direct_to_template(request, 'mikepages/page_diff.html', 
                                          {'page1': page_old, 'page2': page})
            return show(request, page.slug)
    else:
        form = PageForm(instance = page)
    return direct_to_template(request, 'mikepages/page_edit.html', {'form': form})
