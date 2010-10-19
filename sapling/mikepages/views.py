from django.shortcuts import render_to_response

from models import Page

def diff(request):
    pages = Page.objects.all()
    page1 = pages[0]
    page2 = pages[1]
    return render_to_response('page_diff.html', {'page1': page1, 'page2': page2})