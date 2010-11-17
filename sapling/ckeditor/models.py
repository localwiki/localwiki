import os
from lxml import etree
from django.db import models
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _
from StringIO import StringIO


class XMLField(models.TextField):
    description = _("XML text")

    def __init__(self, verbose_name=None, name=None, schema_path=None, **kwargs):
        self.schema_path = schema_path
        models.Field.__init__(self, verbose_name, name, **kwargs)
        
    def validate(self, value, model_instance):
        try:
            relaxng_doc = etree.parse(self.schema_path)
            relaxng = etree.RelaxNG(relaxng_doc)
            doc = etree.parse(StringIO(value))
            if relaxng.validate(doc):
                return
        except:
            pass
        raise exceptions.ValidationError(_('This field contains invalid data.'))
    
    

class HTMLField(XMLField):
    schema_path = os.path.join(os.path.dirname(__file__),'schema','html.ng')
    
    def __init__(self, verbose_name=None, name=None, **kwargs):
        super(HTMLField, self).__init__(verbose_name, name, 
                                        self.schema_path, **kwargs)
    