from urlparse import urljoin

try:
    import simplejson as json
except ImportError:
    import json
    
from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

ckeditor_path = 'js/ckeditor/ckeditor.js'
if settings.DEBUG:
    ckeditor_path = 'js/ckeditor/ckeditor_source.js'

class CKEditor(forms.Textarea):
    _button_map = (('Form', 'form'),
                   ('Checkbox', 'input'),
                   ('Radio', 'input'),
                   ('TextField', 'input'),
                   ('Textarea', 'textarea'),
                   ('Select', 'select'),
                   ('Button', 'input'),
                   ('ImageButton', 'input'),
                   ('Hidden', 'input'),
                   ('Bold', 'strong'),
                   ('Italic', 'em'),
                   ('Underline', 'u'),
                   ('Strike', 'strike'),
                   ('Subscript', 'sub'),
                   ('Superscript', 'sup'),
                   ('NumberedList', 'ol'),
                   ('BulletedList', 'ul'),
                   ('Blockquote', 'blockquote'),
                   ('CreateDiv', 'div'),
                   ('Link', 'a'),
                   ('Unlink', 'a'),
                   ('Anchor', 'a'),
                   ('Image', 'img'),
                   ('Flash', 'object'),
                   ('Table', 'table'),
                   ('HorizontalRule', 'hr'),
                   )
    
    def __init__(self, *args, **kwargs):
        super(CKEditor, self).__init__(*args, **kwargs)
        if 'attrs' in kwargs:
            attrs = kwargs['attrs']
            if 'buttons' in attrs:
                self.config = self.default_config(attrs['buttons'])
                
    def default_config(self, buttons = None):
        toolbar = []
        if buttons:
            for name, tag in self._button_map:
                if tag in buttons:
                    toolbar.append(name)
                    
        return json.dumps({'toolbar': [toolbar]})
                
    def button_for_tag(self, tag):
        if tag in self._button_map:
            return self._button_map[tag]
        else:
            return None
                
    def render(self, name, value, attrs=None, **kwargs):
        rendered = super(CKEditor, self).render(name, value, attrs)
        context = {
            'name': name,
            'config': self.config 
        }
        return rendered +  mark_safe(render_to_string(
            'ckeditor/ckeditor_script.html', context
        ))

    class Media:
        js = (
                urljoin(settings.MEDIA_URL, ckeditor_path),  
        )
