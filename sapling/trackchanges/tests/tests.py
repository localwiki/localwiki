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

mgr = TestSettingsManager()
INSTALLED_APPS=list(settings.INSTALLED_APPS)
INSTALLED_APPS.append('trackchanges.tests')
mgr.set(INSTALLED_APPS=INSTALLED_APPS)

class TrackChangesTest(TestCase):
    def _create_test_models(self):
        """
        Creates some instances of the test models.
        No explicit history here - just the initial models.
        """
        m = M1(a="A!", b="B!", c="C!", d="D!")
        m.save()
        m = M1(a="A2!", b="B2!", c="C2!", d="D2!")
        m.save()

        m = M2(a="Aomg!", b="B! Long text field! Long long long!", c=666)
        m.save()

        m = M3BigInteger(a="Aomg!Big", b=True, c=12345678910111213)
        m.save()

        m = M4Date()
        m.save()

        m = M5Decimal(a=Decimal("1111111111333.123"), b=Decimal("45.1"))
        m.save()

        m = M6Email(a="testing@example.org")
        m.save()

        m = M7Numbers(a=3.14, b=10, c=11, d=4)
        m.save()

        m = M8Time()
        m.save()

        m = M9URL(a="http://example.org/")
        m.save()

        m = M12ForeignKeys(a=M2.objects.all()[0], b="hello!")
        m.save()

        m1 = M13ForeignKeySelf(a=None, b="Something here!")
        m1.save()
        m = M13ForeignKeySelf(a=m1, b="New stuff here!")
        m.save()

        category = Category(a="Master category")
        category.save()
        m = M14ManyToMany(a="text test!")
        m.save()
        m.b.add(category)
        m.save()

        thing = LongerNameOfThing(a="long name")
        thing.save()
        m = M15OneToOne(a="m15 yay!", b=thing)
        m.save()

        m = M16Unique(a="What", b="lots of text", c=6)
        m.save()

    def _setup_file_environment(self):
        fpath = os.path.join(settings.MEDIA_ROOT, 'test_trackchanges_uploads')
        if not os.path.exists(fpath):
            os.mkdir(fpath)
        # remove any existing files
        for name in os.listdir(fpath):
            os.remove(os.path.join(fpath, name))

    def _cleanup_file_environment(self):
        pass

    def all_objects(self):
        objs = []
        for M in self.test_models:
            objs += M.objects.all()
        return objs
    
    def setUp(self):
        self._setup_file_environment()
        self.test_models = TEST_MODELS
        self._create_test_models()

    def tearDown(self):
        """
        Remove all created models and all model history.
        """
        for M in self.test_models:
            for m in M.objects.all():
                # clear out existing history
                for entry in m.history.all():
                    entry.delete()
                m.history.track_changes = False
                m.delete()
                m.history.track_changes = True
        self._cleanup_file_environment()

    def test_new_save(self):
        new_m = M1(a="ayesyes!", b="bbb", c="cx", d="dddd")
        new_m.save()
        self.assertEqual(len(new_m.history.all()), 1)

    def test_empty_save(self):
        history_before = {}
        for m in self.all_objects():
            history_before[m] = (m, len(m.history.all()))
        for m in self.all_objects():
            m.save()
        for m in self.all_objects():
            # saving should add a single history entry
            old_m, old_m_history_len = history_before[m]
            self.assertEqual(len(m.history.all()), old_m_history_len+1)

    def test_most_recent(self):
        m = M1.objects.get(a="A!")
        m_old = copy.copy(m)
        m.b = "Bnew!"
        m.save()

        self.assertEqual(m.history.most_recent().a, m_old.a)
        self.assertEqual(m.history.most_recent().b, "Bnew!")
        self.assertEqual(m.history.most_recent().c, m_old.c)
        self.assertEqual(m.history.most_recent().d, m_old.d)
        self.assertEqual(m.history.most_recent().history_meta.object.b, "Bnew!")

        recent_obj = m.history.most_recent().history_meta.object
        vals_recent = [ getattr(recent_obj, field)
                        for field in recent_obj._meta.get_all_field_names()
        ]
        vals_old = [ getattr(m_old, field)
                     for field in m_old._meta.get_all_field_names()
        ]
        vals = [ getattr(m, field) for field in m._meta.get_all_field_names() ]
        self.assertEqual(
            vals_recent,
            vals
        )
        self.assertNotEqual(
            vals_recent,
            vals_old
        )

    def test_deleted_object(self):
        """
        Delete objects should appear in history.
        """
        m = M16Unique.objects.get(a="What")
        m.delete()
        del_m = m.history.most_recent()
        del_m_obj = del_m.history_meta.object

        self.assertEqual(del_m.history_meta.type, '-')
        self.assertEqual(del_m_obj.a, m.a)
        self.assertEqual(del_m_obj.b, m.b)
        self.assertEqual(del_m_obj.c, m.c)

    def test_deleted_object_lookup(self):
        """
        If we delete an object we should be able to retrieve it.
        """
        m = M16Unique.objects.get(a="What")
        m.b = "This is the new long text"
        m.save()
        m.delete()
        del m

        # A filter on the unique field should do the trick
        history_entries = M16Unique.history.filter(a="What")
        m = history_entries[0].history_meta.object
        self.assertEqual(m.a, "What")
        self.assertEqual(m.b, "This is the new long text")
        del m

        # And we should also be able to look up based on a new object
        # with the same unique fields
        m = M16Unique(a="What", b="something else")
        self.assertEqual(m.history.all()[0].a, "What")
        self.assertEqual(m.history.all()[0].b, "This is the new long text")

    def test_deleted_object_recreate(self):
        """
        Creating a once-deleted object again with the same unique
        fields should cause the history to behave as if it's the same
        object.
        """
        m = M16Unique.objects.get(a="What")
        m.b = "This is the new long text"
        m.save()
        m.delete()
        old_history_len = len(m.history.all())
        del m
        m2 = M16Unique(a="Something", b="Else", c=75)
        m2.save()

        # What if we create a new model with the same unique field?
        m = M16Unique(a="What", b="NEWEST text here!", c=34)
        m.save()

        # When we look up the history, there should be entries for the older,
        # now deleted object included.

        # all the history entries should have the same unique field
        self.assertEqual([x.a for x in m.history.all()],
                         ["What"]*len(m.history.all())
        )
        # and the history should be old_history_len+1 entries long
        self.assertEqual(len(m.history.all()), old_history_len+1)

    def test_deleted_object_nonunique(self):
        """
        When we delete an object without any unique fields and then create a new object
        with the same attributes, right afterward, we should see an entirely new history.
        """
        m = M2(a="new m2!", b="text", c=54)
        m.save()
        m.b = "new text!"
        m.save()
        m.delete()

        m2 = M2(a="new m2!", b="new text!", c=54)
        m2.save()

        self.assertEqual(len(m2.history.all()), 1)

    def test_deleted_file(self):
        m = M10File()
        m.a.save("a.txt", ContentFile("TEST FILE"), save=False)
        m.save()
        path = m.a.path
        self.assertTrue(os.path.exists(path))
        m.a.delete()
        self.assertTrue(os.path.exists(path))

        im_src = os.path.join(os.path.split(__file__)[0], 'static', 'a.png')
        im_dest = os.path.join(
            settings.MEDIA_ROOT, 'test_trackchanges_uploads', 'a.png'
        )
        m = M11Image(a=File(open(im_src, 'r')))
        m.save()
        path = m.a.path
        self.assertTrue(os.path.exists(path))
        m.a.delete()
        self.assertTrue(os.path.exists(path))

    def test_version_numbering(self):
        m = M2(a="Newz!", b="B!", c=666)
        m.save()
        for i in range(1, 100):
            v_cur = m.history.most_recent()
            date = v_cur.history_meta.date
            self.assertEqual(v_cur.history_meta.get_version_number(), i)
            m.b += "."
            m.save()

    def test_version_number_grab(self):
        m = M2(a="Yay versioning!", b="Hey!", c=1)
        m.save()
        for i in range(1, 100):
            # version numbers should line up with m.c value now
            m.c = i+1
            m.save()

        for i in range(1, 100):
            m_old = m.history.as_of(version=i)
            self.assertEqual(m_old.c, i)

    def test_version_date_grab(self):
        m = M2(a="Yay versioning!", b="Hey!", c=1)
        m.save()
        for i in range(1, 20):
            # day of month should line up with m.c value now
            m.c = i
            m.history.save_with(date=datetime.datetime(2010, 10, i))
            m.save()

        # exact dates
        for i in range(1, 20):
            m_old = m.history.as_of(date=datetime.datetime(2010, 10, i))
            self.assertEqual(m_old.c, i)

        # a date in-between two revisions should yield the earlier revision
        for i in range(1, 20):
            m_old = m.history.as_of(date=datetime.datetime(2010, 10, i, 10))
            self.assertEqual(m_old.c, i)
