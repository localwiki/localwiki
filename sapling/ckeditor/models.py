import os
from lxml import etree
import html5lib
from html5lib import sanitizer

from django.db import models
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _
from StringIO import StringIO
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
    
class MySanitizer(sanitizer.HTMLSanitizer):
    allowed_elements = ['p', 'a']

def sanitize_html(unsafe):
    p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
    tree = p.parse(unsafe)
    return tree.toxml()

def sanitize_html_fragment(unsafe):
    p = html5lib.HTMLParser(tokenizer=MySanitizer)
    tree = p.parseFragment(unsafe)
    return tree.toxml()

class XMLField(models.TextField):
    description = _("XML text")

    def __init__(self, verbose_name=None, name=None, schema_path=None, **kwargs):
        self.schema_path = schema_path
        self.default_validators = [XMLValidator(schema_path)]
        models.Field.__init__(self, verbose_name, name, **kwargs)
    
    
class XHTMLField(XMLField):
    ''' Note: this needs a real schema document before it will work! '''
    description = _("XHTML text")
    schema_path = os.path.join(os.path.dirname(__file__),'schema','html.ng')
    
    def __init__(self, verbose_name=None, name=None, **kwargs):
        super(XHTMLField, self).__init__(verbose_name, name, 
                                        self.schema_path, **kwargs)

class HTML5Field(models.TextField):
    description = _("HTML5 text")
    
    def __init(self, verbose_name=None, name=None, **kwargs):
        models.Field.__init__(self, verbose_name, name, **kwargs)
        
    def clean(self, value, model_instance):
        super(HTML5Field, self).clean(value, model_instance)
        return sanitize_html(value)
    
class HTML5FragmentField(models.TextField):
    description = _("HTML5 fragment text")
    
    def __init(self, verbose_name=None, name=None, **kwargs):
        models.Field.__init__(self, verbose_name, name, **kwargs)
        
    def clean(self, value, model_instance):
        super(HTML5FragmentField, self).clean(value, model_instance)
        return sanitize_html_fragment(value)
    
    def formfield(self, **kwargs):
        defaults = {'widget' : widgets.CKEditor}
        defaults.update(kwargs)
        return super(HTML5FragmentField, self).formfield(**defaults)