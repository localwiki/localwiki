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
from models import M1, M2, TEST_MODELS

import modeldiff
from modeldiff import *

mgr = TestSettingsManager()
INSTALLED_APPS=list(settings.INSTALLED_APPS)
INSTALLED_APPS.append('modeldiff.tests')
mgr.set(INSTALLED_APPS=INSTALLED_APPS)

class ModelDiffTest(TestCase):
    
    def setUp(self):
        self.test_models = TEST_MODELS

    def tearDown(self):
        pass
    
    def test_identical_models(self):
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

class BaseFieldDiffTest(TestCase):
    
    def test_identical_fields(self):
        '''
        The diff between two identical fields of any type should be None
        '''
        vals = ['Lorem', 123, True, datetime.datetime.now()]
        for v in vals:
            d = BaseFieldDiff(v, v)
            self.assertEqual(d.as_dict(), None)

        
    def test_identical_fields_html(self):
        '''
        The html of the diff between two identical fields should be readable message
        '''
        a = 'Lorem'
        d = BaseFieldDiff(a, a)
        self.assertTrue("No differences" in d.as_html())
        
class DiffRegistryTest(TestCase):
    
    def test_can_handle_any_field(self):
        '''
        Out of the box, the registry should offer diff utils for any field
        '''
        r = modeldiff.diffutils.registry
        field_types = [db.models.CharField, db.models.TextField, db.models.BooleanField]
        for t in field_types:
            d = r.get_diff_util(t)
            self.assertTrue(issubclass(d, BaseFieldDiff))
    
    def test_can_handle_any_model(self):
        '''
        Out of the box, the registry should offer diff utils for any model
        '''
        r = modeldiff.diffutils.registry
        for t in TEST_MODELS:
            d = r.get_diff_util(t)
            self.assertTrue(issubclass(d, BaseModelDiff))
            
    def test_register_model(self):
        '''
        If we register a modeldiff for a model, we should get that and not BaseModelDiff
        '''
        