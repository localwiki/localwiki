from urlparse import urljoin

from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class CKEditor(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super(CKEditor, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, **kwargs):
        rendered = super(CKEditor, self).render(name, value, attrs)
        context = {
            'name': name,
        }
        return rendered +  mark_safe(render_to_string(
            'ckeditor/ckeditor_script.html', context
        ))

    class Media:
        js = (
            urljoin(settings.MEDIA_URL, '/js/ckeditor/ckeditor.js'),
        )
