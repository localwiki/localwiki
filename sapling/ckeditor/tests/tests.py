from django.test import TestCase
from django.db import models
from django.core import exceptions

from ckeditor.models import HTMLField, XMLField
import os

class TestModel(models.Model):
    html = HTMLField()

class WikiContentsFieldTest(TestCase):
    
    def test_html_schema_set(self):
        html = HTMLField()
        self.assertTrue(isinstance(html, XMLField))
        self.assertEquals(html.schema_path, HTMLField.schema_path)
    
    def test_html_schema_exists(self):
        self.assertTrue(os.path.exists(HTMLField.schema_path))
        
    def test_valid_html(self):
        m = TestModel()
        m.html = '<html><head><title>Lorem</title></head><body>Ipsum</body></html>'
        m.clean_fields()
        
    def test_invalid_html(self):
        m = TestModel()
        m.html = 'invalid html'
        self.assertRaises(exceptions.ValidationError, m.clean_fields)