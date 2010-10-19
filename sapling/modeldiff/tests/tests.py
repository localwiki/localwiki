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

from utils import TestSettingsManager
from models import *

from modeldiff.diffutils import *



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
        vals = { 'a': 'Lorem', 'b': 'Ipsum', 'c': datetime.datetime.now()}
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
        a = 'Lorem'
        d = BaseFieldDiff(a, a)
        self.assertEqual(d.as_dict(), None)
        
        a = 123
        d = BaseFieldDiff(a, a)
        self.assertEqual(d.as_dict(), None)
        
        a = datetime.datetime.now()
        d = BaseFieldDiff(a, a)
        self.assertEqual(d.as_dict(), None)
        
    def test_identical_fields_html(self):
        '''
        The html of the diff between two identical fields should be readable message
        '''
        a = 'Lorem'
        d = BaseFieldDiff(a, a)
        self.assertTrue("No differences" in d.as_html())