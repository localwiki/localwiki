import os
from StringIO import StringIO
from lxml import etree
import html5lib
from html5lib import sanitizer, treebuilders
from xml.sax.saxutils import escape

from django.db import models
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _

import widgets


class XMLValidator(object):
    def __init__(self, schema_path):
        self.schema_path = schema_path

    def __call__(self, value):
        try:
            relaxng_doc = etree.parse(self.schema_path)
            relaxng = etree.RelaxNG(relaxng_doc)
            doc = etree.parse(StringIO(value))
            if relaxng.validate(doc):
                return
        except:
            pass
        raise exceptions.ValidationError('This field contains invalid data.')


def custom_sanitizer(allowed):
    class CustomSanitizer(sanitizer.HTMLSanitizer):
        allowed_elements = allowed

    return CustomSanitizer


def sanitize_html(unsafe):
    p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
    tree = p.parse(unsafe)
    return tree.toxml()


def sanitize_html_fragment(unsafe, allowed_elements=None, encoding='UTF-8'):
    # TODO: make this more simple / understandable and factor out from
    # plugins.html_to_template_text
    if not allowed_elements:
        allowed_elements = sanitizer.HTMLSanitizer.allowed_elements
    p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("lxml"),
                            tokenizer=custom_sanitizer(allowed_elements),
                            namespaceHTMLElements=False)
    top_level_elements = p.parseFragment(unsafe, encoding=encoding)
    # put top level elements in container
    container = etree.Element('div')
    if top_level_elements and not hasattr(top_level_elements[0], 'tag'):
        container.text = top_level_elements.pop(0)
    container.extend(top_level_elements)

    html_bits = [etree.tostring(elem, method='html', encoding=encoding)
                     for elem in container]

    return ''.join([escape(container.text or '').encode(encoding)] + html_bits)


class XMLField(models.TextField):
    description = _("XML text")

    def __init__(self, verbose_name=None, name=None, schema_path=None, **kws):
        self.schema_path = schema_path
        self.default_validators = [XMLValidator(schema_path)]
        models.Field.__init__(self, verbose_name, name, **kws)


class XHTMLField(XMLField):
    """Note: this needs a real schema document before it will work!"""
    description = _("XHTML text")
    schema_path = os.path.join(os.path.dirname(__file__), 'schema', 'html.ng')

    def __init__(self, verbose_name=None, name=None, **kwargs):
        super(XHTMLField, self).__init__(verbose_name, name,
                                        self.schema_path, **kwargs)


class HTML5Field(models.TextField):
    description = _("HTML5 text")

    def __init__(self, verbose_name=None, name=None, **kwargs):
        models.Field.__init__(self, verbose_name, name, **kwargs)

    def clean(self, value, model_instance):
        super(HTML5Field, self).clean(value, model_instance)
        return sanitize_html(value)


class HTML5FragmentField(models.TextField):
    """
    Use this field in your models for storing user-editable HTML fragments.
    It provides the CKEditor widget by default and sanitizes user-submitted
    HTML before storing it using html5lib.
    Any non-whitelisted elements, such as <script>, will be escaped, and non-
    whitelisted attributes will be stripped.
    You can customize the whitelisted elements by setting the allowed_elements
    argument like this:

    class Page(models.Model):
        contents = HTML5FragmentField(
            allowed_elements=['p', 'a', 'strong', 'em']
        )
    """
    description = _("HTML5 fragment text")
    encoding = 'UTF-8'

    def __init__(self, verbose_name=None, name=None, allowed_elements=None,
                 **kwargs):
        models.Field.__init__(self, verbose_name, name, **kwargs)
        self.allowed_elements = allowed_elements

    def clean(self, value, model_instance):
        value = super(HTML5FragmentField, self).clean(value, model_instance)
        return sanitize_html_fragment(value, self.allowed_elements,
                                      encoding=self.encoding)

    def formfield(self, **kwargs):
        defaults = {
            'widget': widgets.CKEditor(allowed_tags=self.allowed_elements)
        }
        defaults.update(kwargs)
        return super(HTML5FragmentField, self).formfield(**defaults)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^ckeditor\.models"])
except ImportError:
    pass
