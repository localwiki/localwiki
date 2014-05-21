from django import forms
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.template.loader import render_to_string

from utils.static_helpers import static_url


class TagEdit(forms.TextInput):
    def autocomplete_url(self):
        return ('/_api/tags/suggest/')

    def render(self, name, value, attrs=None):
        input = super(TagEdit, self).render(name, value, attrs)
        return input + render_to_string('tags/tagedit.html',
                                        {'id': attrs['id'],
                                         'autocomplete_url': self.autocomplete_url()
                                         })

    class Media:
        js = (static_url('tagedit/js/jquery.tagedit.js'),
              static_url('tagedit/js/jquery.autoGrowInput.js'),
              static_url('js/jquery/jquery-ui-1.8.16.custom.min.js'),
        )
        css = { 'all':
            (static_url('tagedit/css/jquery.tagedit.css'),
             static_url('tagedit/css/ui-lightness/jquery-ui-1.8.6.custom.css'),
            ),
        }
