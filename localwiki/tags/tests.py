# coding=utf-8

from django.test import TestCase
from tags.models import Tag
from django.db import IntegrityError


class TagTest(TestCase):
    def test_bad_tags(self):
        t = Tag(name='')
        self.failUnlessRaises(IntegrityError, t.save, t)

        t = Tag(name='!')
        self.failUnlessRaises(IntegrityError, t.save, t)

        t = Tag(name='/')
        self.failUnlessRaises(IntegrityError, t.save, t)

        t = Tag(name=' ')
        self.failUnlessRaises(IntegrityError, t.save, t)

        t = Tag(name='-')
        self.failUnlessRaises(IntegrityError, t.save, t)

        t = Tag(name='!@#$%^&*()')
        self.failUnlessRaises(IntegrityError, t.save, t)

    def test_slug(self):
        t = Tag(name='Library of Congress')
        t.save()
        self.assertEqual(t.slug, 'libraryofcongress')

        t = Tag(name='Сочи 2014')
        t.save()
        self.assertEqual(t.slug, 'сочи2014'.decode('utf-8'))
