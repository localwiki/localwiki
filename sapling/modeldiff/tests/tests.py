import os
import copy
import shutil
import datetime
from decimal import Decimal
import cStringIO as StringIO
from pprint import pprint

from django.test import TestCase, Client
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django import db

from utils import TestSettingsManager
from models import M1, M1Diff, M1FieldDiff, M2, M3, TEST_MODELS

import modeldiff
from modeldiff.diffutils import Registry, BaseFieldDiff, BaseModelDiff
from modeldiff.diffutils import TextFieldDiff, FileFieldDiff, ImageFieldDiff

mgr = TestSettingsManager()
INSTALLED_APPS=list(settings.INSTALLED_APPS)
INSTALLED_APPS.append('modeldiff.tests')
mgr.set(INSTALLED_APPS=INSTALLED_APPS)

class ModelDiffTest(TestCase):
    
    def setUp(self):
        self.test_models = TEST_MODELS

    def tearDown(self):
        pass
    
    def test_identical(self):
        '''
        The diff between two identical models, or a model and itself should be None
        '''
        vals = { 'a': 'Lorem', 'b': 'Ipsum', 'c': datetime.datetime.now(), 'd': 123}
        m1 = M1.objects.create(**vals)
        m2 = M1.objects.create(**vals)
    
        d = modeldiff.diff(m1, m1).as_dict()
        self.assertEqual(d, None)
        
        d = modeldiff.diff(m1, m2).as_dict()
        self.assertEqual(d, None)
    
    def test_nearly_identical(self):
        '''
        The diff between models should consist of only the fields that are different
        '''
        vals = { 'a': 'Lorem', 'b': 'Ipsum', 'c': datetime.datetime.now(), 'd': 123}
        m1 = M1.objects.create(**vals)
        vals['a'] = 'Ipsum'
        m2 = M1.objects.create(**vals)
        d = modeldiff.diff(m1, m2).as_dict()
        self.assertTrue(len(d) == 1)

class BaseFieldDiffTest(TestCase):
    test_class = BaseFieldDiff
    
    def test_identical_fields_dict(self):
        '''
        The diff between two identical fields of any type should be None
        '''
        vals = ['Lorem', 123, True, datetime.datetime.now()]
        for v in vals:
            d = self.test_class(v, v)
            self.assertEqual(d.as_dict(), None)

        
    def test_identical_fields_html(self):
        '''
        The html of the diff between two identical fields should be sensible message
        '''
        a = 'Lorem'
        d = self.test_class(a, a).as_html()
        self.assertTrue("No differences" in d)
        
    def test_deleted_inserted(self):
        a = 123
        b = 456
        d = self.test_class(a, b).as_dict()
        self.assertTrue(d['deleted'] == a)
        self.assertTrue(d['inserted'] == b)
        
class TextFieldDiffTest(BaseFieldDiffTest):
    test_class = TextFieldDiff
    
    def test_deleted_inserted(self):
        a = 'abc'
        b = 'def'
        d = self.test_class(a, b).as_dict()
        self.assertTrue(len(d) == 2)
        self.assertTrue(d[0]['deleted'] == a)
        self.assertTrue(d[1]['inserted'] == b)
    
    def test_equal(self):
        a = 'abcdef'
        b = 'abcghi'
        d = self.test_class(a, b).as_dict()
        self.assertTrue(len(d) == 3)
        self.assertTrue(d[0]['equal'] == 'abc')

class FileFieldDiffTest(BaseFieldDiffTest):
    test_class = FileFieldDiff
    
    def test_deleted_inserted(self):
        m1 = M2()
        m1.a.save("a.txt", ContentFile("TEST FILE"), save=False)
        
        m2 = M2()
        m2.a.save("b.txt", ContentFile("TEST FILE"), save=False)
        
        d = self.test_class(m1.a, m2.a).as_dict()
        self.assertTrue(d['name']['deleted'] == m1.a.name)
        self.assertTrue(d['name']['inserted'] == m2.a.name)
        
        m1.a.delete()
        m2.a.delete()

class ImageFieldDiffTest(FileFieldDiffTest):
    test_class = ImageFieldDiff
        
class DiffRegistryTest(TestCase):
    
    def setUp(self):
        self.registry = Registry()
        
        vals = { 'a': 'Lorem', 'b': 'Ipsum', 'c': datetime.datetime.now(), 'd': 123}
        m1 = M1.objects.create(**vals)
    
    def test_can_handle_any_field(self):
        '''
        Out of the box, the registry should offer diff utils for any field
        '''
        r = self.registry
        field_types = [db.models.CharField, db.models.TextField, db.models.BooleanField]
        for t in field_types:
            d = r.get_diff_util(t)
            self.assertTrue(issubclass(d, BaseFieldDiff))
    
    def test_can_handle_any_model(self):
        '''
        Out of the box, the registry should offer diff utils for any model
        '''
        r = self.registry
        for t in TEST_MODELS:
            d = r.get_diff_util(t)
            self.assertTrue(issubclass(d, BaseModelDiff))          
    
    def test_fallback_diff(self):
        class AwesomeImageField(db.models.ImageField):
            pass
        '''
        If we don't have a diff util for the exact field type, we should fall back to the
        diff util for the base class, until we find a registered util
        '''
        self.registry.register(db.models.FileField, FileFieldDiff)
        d = self.registry.get_diff_util(AwesomeImageField)
        self.assertTrue(issubclass(d, FileFieldDiff))
        
    def test_register_model(self):
        '''
        If we register a modeldiff for a model, we should get that and not BaseModelDiff
        '''
        self.registry.register(M1, M1Diff)
        self.failUnlessEqual(self.registry.get_diff_util(M1), M1Diff)
    
    def test_register_field(self):
        '''
        If we register a fielddiff for a model, we should get that and not BaseFieldDiff
        '''
        self.registry.register(db.models.CharField, M1FieldDiff)
        self.failUnlessEqual(self.registry.get_diff_util(db.models.CharField), M1FieldDiff)
        
    def test_cannot_diff_something_random(self):
        '''
        If we try to diff something that is neither a model nor a field, raise exception.
        '''
        self.failUnlessRaises(modeldiff.diffutils.DiffUtilNotFound, self.registry.get_diff_util, DiffRegistryTest)
    