import os
import re
from StringIO import StringIO
from lxml import etree
import html5lib
from html5lib import sanitizer, treebuilders
from html5lib.constants import tokenTypes
from xml.sax.saxutils import escape, unescape

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


class HTMLSanitizer(sanitizer.HTMLSanitizer):
    allowed_attributes_map = None
    allowed_styles_map = None

    def sanitize_token(self, token):
        """"
        An adaptation of sanitizer.HTMLSanitizer.sanitize_token that enforces
        particular values for allowed attributes.  We use the class variables
        allowed_attributes_map and allowed_styles_map, which are of the form:

            allowed_attributes_map = {'a': ['class', 'href'], 'img': ['style']}

            allowed_styles_map = {'img': ['width', 'height']}
        """
        if token["type"] in (tokenTypes["StartTag"], tokenTypes["EndTag"],
                             tokenTypes["EmptyTag"]):
            if token["name"] in self.allowed_elements:
                tag = token["name"]
                if "data" in token:
                    allowed_attrs = self.allowed_attributes
                    if self.allowed_attributes_map:
                        allowed_attrs = self.allowed_attributes_map.get(tag,
                                                                        [])
                    attrs = dict([(name, val) for name, val in
                                  token["data"][::-1]
                                  if name in allowed_attrs])
                    for attr in self.attr_val_is_uri:
                        if not attr in attrs:
                            continue
                        val_unescaped = re.sub("[`\000-\040\177-\240\s]+", '',
                                               unescape(attrs[attr])).lower()
                        #remove replacement characters from unescaped chars
                        val_unescaped = val_unescaped.replace(u"\ufffd", "")
                        if (re.match("^[a-z0-9][-+.a-z0-9]*:", val_unescaped)
                            and (val_unescaped.split(':')[0] not in
                                 self.allowed_protocols)):
                            del attrs[attr]
                    for attr in self.svg_attr_val_allows_ref:
                        if attr in attrs:
                            attrs[attr] = re.sub(r'url\s*\(\s*[^#\s][^)]+?\)',
                                                 ' ',
                                                 unescape(attrs[attr]))
                    if (token["name"] in self.svg_allow_local_href and
                        'xlink:href' in attrs and re.search('^\s*[^#\s].*',
                                                        attrs['xlink:href'])):
                        del attrs['xlink:href']
                    if 'style' in attrs:
                        attrs['style'] = self.sanitize_css(attrs['style'])
                        if self.allowed_styles_map:
                            ok_styles = self.allowed_styles_map.get(tag, [])
                            attrs['style'] = self.filter_styles(
                                                            attrs['style'],
                                                            ok_styles)
                    token["data"] = [[k, v] for k, v in attrs.items()]
                return token
            else:
                if token["type"] == tokenTypes["EndTag"]:
                    token["data"] = "</%s>" % token["name"]
                elif token["data"]:
                    attrs = ''.join([' %s="%s"' % (k, escape(v))
                                     for k, v in token["data"]])
                    token["data"] = "<%s%s>" % (token["name"], attrs)
                else:
                    token["data"] = "<%s>" % token["name"]
                if token["selfClosing"]:
                    token["data"] = token["data"][:-1] + "/>"
                token["type"] = tokenTypes["Characters"]
                del token["name"]
                return token
        elif token["type"] == tokenTypes["Comment"]:
            pass
        else:
            return token

    def filter_styles(self, css, ok_styles):
        styles = parse_style(css)
        styles = dict((k, v) for k, v in styles.iteritems() if k in ok_styles)
        return ' '.join(['%s: %s;' % (k, v) for k, v in styles.iteritems()])


def parse_style(css):
    """
    Parses style attribute string into dictionary
    """
    style = {}
    for line in css.split(';'):
        try:
            bits = line.split(':')
            style[bits[0].strip()] = ':'.join(bits[1:]).strip()
        except:
            pass
    return style


def custom_sanitizer(elements, attribute_map, styles_map):
    class CustomSanitizer(HTMLSanitizer):
        allowed_elements = elements
        allowed_attributes_map = attribute_map
        allowed_styles_map = styles_map

    return CustomSanitizer


def sanitize_html(unsafe):
    p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
    tree = p.parse(unsafe)
    return tree.toxml()


def sanitize_html_fragment(unsafe, allowed_elements=None,
        allowed_attributes_map=None, allowed_styles_map=None,
        encoding='UTF-8'):
    # TODO: make this more simple / understandable and factor out from
    # plugins.html_to_template_text
    if not allowed_elements:
        allowed_elements = sanitizer.HTMLSanitizer.allowed_elements

    tokenizer = custom_sanitizer(allowed_elements, allowed_attributes_map,
                               allowed_styles_map)
    p = html5lib.HTMLParser(
        tree=treebuilders.getTreeBuilder("lxml"),
        tokenizer=tokenizer,
        namespaceHTMLElements=False
    )
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
    whitelisted attributes and styles will be stripped.
    You can customize the whitelisted elements, attributes, and styles by
    setting the allowed_elements, allowed_attributes_map, and
    allowed_styles_map argument like this:

    class Page(models.Model):
        contents = HTML5FragmentField(
            allowed_elements=['p', 'a', 'strong', 'em'],
            allowed_attributes_map={'p': ['style'], 'a': ['href', 'name']},
            allowed_styles_map={'p': ['text-align', 'font-size']}
        )

    All of these are optional, and, when missing, imply anything is allowed.
    """
    description = _("HTML5 fragment text")
    encoding = 'UTF-8'

    def __init__(self, verbose_name=None, name=None, allowed_elements=None,
                 allowed_attributes_map=None, allowed_styles_map=None,
                 **kwargs):
        models.Field.__init__(self, verbose_name, name, **kwargs)
        self.allowed_elements = allowed_elements
        self.allowed_attributes_map = allowed_attributes_map
        self.allowed_styles_map = allowed_styles_map

    def clean(self, value, model_instance):
        value = super(HTML5FragmentField, self).clean(value, model_instance)
        return sanitize_html_fragment(value, self.allowed_elements,
                                      self.allowed_attributes_map,
                                      self.allowed_styles_map,
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
