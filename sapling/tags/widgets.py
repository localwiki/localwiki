from django import forms
from utils.static import static_url
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.template.loader import render_to_string


class TagEdit(forms.TextInput):
    def render(self, name, value, attrs=None):
        input = super(TagEdit, self).render(name, value, attrs)
        return input + render_to_string('tags/tagedit.html',
                                        {'id': attrs['id']})

    class Media:
        js = (static_url('js/jquery/jquery-1.7.min.js'),
              static_url('tagedit/js/jquery.tagedit.js'),
              static_url('tagedit/js/jquery.autoGrowInput.js'),
              static_url('js/jquery/jquery-ui-1.8.16.custom.min.js'),
        )
