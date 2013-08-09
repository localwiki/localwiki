# coding=utf-8

from django.test import TestCase
from django.db import IntegrityError

from regions.models import Region
from tags.models import Tag


class TagTest(TestCase):
    def setUp(self):
        self.region = Region(full_name='Test Region', slug='test_region')
        self.region.save()
        
    def test_bad_tags(self):
        t = Tag(name='', region=self.region)
        self.failUnlessRaises(IntegrityError, t.save, t)

        t = Tag(name='!', region=self.region)
        self.failUnlessRaises(IntegrityError, t.save, t)

        t = Tag(name='/', region=self.region)
        self.failUnlessRaises(IntegrityError, t.save, t)

        t = Tag(name=' ', region=self.region)
        self.failUnlessRaises(IntegrityError, t.save, t)

        t = Tag(name='-', region=self.region)
        self.failUnlessRaises(IntegrityError, t.save, t)

        t = Tag(name='!@#$%^&*()', region=self.region)
        self.failUnlessRaises(IntegrityError, t.save, t)

    def test_slug(self):
        t = Tag(name='Library of Congress', region=self.region)
        t.save()
        self.assertEqual(t.slug, 'libraryofcongress')

        t = Tag(name='Сочи 2014', region=self.region)
        t.save()
        self.assertEqual(t.slug, 'сочи2014'.decode('utf-8'))
