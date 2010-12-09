from django.shortcuts import render_to_response

from models import Page
from forms import PageForm
from django.views.generic.simple import direct_to_template

from django.db.models import AutoField
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

def edit(request, object_id=None):
    page = Page.objects.get(pk=object_id)
    page_old = copy_model_instance(page)
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            return direct_to_template(request, 'mikepages/page_diff.html', {'page1': page_old, 'page2': page})
    else:
        form = PageForm(instance = page)
    return render_to_response('mikepages/page_edit.html', {'form': form})