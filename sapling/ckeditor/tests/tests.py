import os

from django.test import TestCase
from django.db import models
from django.core import exceptions

from ckeditor.models import XHTMLField, XMLField, HTML5Field, HTML5FragmentField
import xssattacks

class XHTMLModel(models.Model):
    html = XHTMLField()
    
class HTML5Model(models.Model):
    html = HTML5Field()
    
class HTML5FragmentModel(models.Model):
    html = HTML5FragmentField()

class XHTMLFieldTest(TestCase):
    def test_html_schema_set(self):
        html = XHTMLField()
        self.assertTrue(isinstance(html, XMLField))
        self.assertEquals(html.schema_path, XHTMLField.schema_path)
    
    def test_html_schema_exists(self):
        self.assertTrue(os.path.exists(XHTMLField.schema_path))
        
    def test_valid_html(self):
        m = XHTMLModel()
        m.html = '<html><head><title>Lorem</title></head><body>Ipsum</body></html>'
        m.clean_fields()
        
    def test_invalid_html(self):
        m = XHTMLModel()
        m.html = 'invalid html'
        self.assertRaises(exceptions.ValidationError, m.clean_fields)

class HTML5FieldTest(TestCase):
    def test_sanitize(self):
        m = HTML5Model()
        m.html = '<html><head/><body><script/></body></html>'
        m.clean_fields()
        self.assertEquals(m.html, '<html><head/><body>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;script/&gt;&lt;/body&gt;&lt;/html&gt;</body></html>')

class HTML5FragmentField(TestCase):
    def test_sanitize(self):
        m = HTML5FragmentModel()
        m.html = '<script/>'
        m.clean_fields()
        self.assertEquals(m.html, '&lt;script/&gt;')
  
class XSSTest(TestCase):
    def test_xss_attacks_xhtml(self):
        for doc in xssattacks.xss_attacks():
            m = XHTMLModel()
            m.html = doc
            print doc
            self.assertRaises(exceptions.ValidationError, m.clean_fields)
