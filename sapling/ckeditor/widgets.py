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
    _auto_button_map = (('Form', 'form'),
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
            self.attrs = kwargs['attrs']
            if 'ck_config' in self.attrs:
                self.config = self.attrs['ck_config'] 

    def get_config(self):
        """Get the config definition for CKEditor.

        Returns:
            Dictionary containing things like 'toolbar', 'plugins', etc.
        """
        if hasattr(self, 'config'):
            return self.config
        config = {}
        config['toolbar'] = self.get_toolbar()
        config['plugins'] = self.get_plugins()
        config['extraPlugins'] = self.get_extra_plugins()
        for k, v in config.items():
            if not v:
                del config[k]
        return config

    def get_toolbar(self):
        """Get the toolbar definition for CKEditor.

        Returns:
            Array of toolbars, each toolbar being an array of button names.
        """
        toolbar = []
        if 'allowed_tags' in self.attrs:
            allowed_tags = self.attrs['allowed_tags']
            for name, tag in self._auto_button_map:
                if tag in allowed_tags:
                    toolbar.append(name)
        return [toolbar]

    def get_plugins(self):
        """Get the comma-separated list of plugins for CKEditor
        """
        return None

    def get_extra_plugins(self):
        """Get the comma-separated list of extra plugins for CKEditor
        """
        return None

    def render(self, name, value, attrs=None, **kwargs):
        rendered = super(CKEditor, self).render(name, value, attrs)
        context = {
            'name': name,
            'config': json.dumps(self.get_config())
        }
        return rendered + mark_safe(render_to_string(
            'ckeditor/ckeditor_script.html', context
        ))

    class Media:
        js = (
                urljoin(settings.STATIC_URL, ckeditor_path),
        )
