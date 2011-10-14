import datetime

from django.test import TestCase
from django.conf import settings
from django.core.files.base import ContentFile
from django import db

from utils import TestSettingsManager
from models import *
from versionutils import diff
from versionutils.diff.diffutils import Registry, BaseFieldDiff, BaseModelDiff
from versionutils.diff.diffutils import TextFieldDiff
from versionutils.diff.diffutils import FileFieldDiff
from versionutils.diff.diffutils import ImageFieldDiff
from versionutils.diff.diffutils import HtmlFieldDiff
from versionutils.diff.diffutils import GeometryFieldDiff

mgr = TestSettingsManager()
INSTALLED_APPS = list(settings.INSTALLED_APPS)
INSTALLED_APPS.append('versionutils.diff.tests')
mgr.set(INSTALLED_APPS=INSTALLED_APPS)


class ModelDiffTest(TestCase):
    def setUp(self):
        self.test_models = TEST_MODELS

    def tearDown(self):
        pass

    def test_identical(self):
        """
        The diff between two identical models, or a model and itself should be
        None.
        """
        vals = {'a': 'Lorem', 'b': 'Ipsum',
                'c': datetime.datetime.now(), 'd': 123}
        m1 = Diff_M1.objects.create(**vals)
        m2 = Diff_M1.objects.create(**vals)

        d = diff.diff(m1, m1).as_dict()
        self.assertEqual(d, None)

        d = diff.diff(m1, m2).as_dict()
        self.assertEqual(d, None)

    def test_nearly_identical(self):
        """
        The diff between models should consist of only the fields that are
        different.
        """
        vals = {'a': 'Lorem', 'b': 'Ipsum',
                'c': datetime.datetime.now(), 'd': 123}
        m1 = Diff_M1.objects.create(**vals)
        vals['a'] = 'Ipsum'
        m2 = Diff_M1.objects.create(**vals)
        d = diff.diff(m1, m2).as_dict()
        self.assertTrue(len(d) == 1)

    def test_foreign_key_identical(self):
        """
        The diff between two ForeignKey fields to the same object should be
        None.
        """
        vals = {'a': 'Lorem', 'b': 'Ipsum',
                'c': datetime.datetime.now(), 'd': 123}
        m1 = Diff_M1.objects.create(**vals)

        m3 = Diff_M4ForeignKey.objects.create(a=m1)
        m4 = Diff_M4ForeignKey.objects.create(a=m1)

        d = diff.diff(m3, m4).as_dict()
        self.assertTrue(d is None)

    def test_foreign_key(self):
        """
        The diff between two ForeignKey fields should be the same as the diff
        between the two objects referenced by the fields
        """
        vals = {'a': 'Lorem', 'b': 'Ipsum',
                'c': datetime.datetime.now(), 'd': 123}
        m1 = Diff_M1.objects.create(**vals)
        vals = {'a': 'Dolor', 'b': 'Ipsum',
                'c': datetime.datetime.now(), 'd': 123}
        m2 = Diff_M1.objects.create(**vals)

        m3 = Diff_M4ForeignKey.objects.create(a=m1)
        m4 = Diff_M4ForeignKey.objects.create(a=m2)

        d1 = diff.diff(m3, m4).as_dict()
        self.assertTrue(d1['a'])

        d2 = diff.diff(m1, m2).as_dict()

        self.assertEqual(d1['a'], d2)

    def test_historical_instance(self):
        o1 = Diff_M5Versioned(a="O1")
        o1.save()
        o2 = Diff_M5Versioned(a="O2")
        o2.save()


class FakeFieldDiffTest(TestCase):
    def test_property_diff(self):
        """
        The "fields" included in a diff don't have to be fields at all and can
        be properties, for example, as long as a custom ModelDiff is registered
        which dictates what FieldDiff to use for the "field".
        """
        diff.register(FakeFieldModel, FakeFieldModelDiff)
        a = FakeFieldModel(a='abc')
        b = FakeFieldModel(a='def')
        d = diff.diff(a, b)
        self.assertTrue(isinstance(d['b'], (TextFieldDiff,)))


class BaseFieldDiffTest(TestCase):
    def setUp(self):
        self.test_class = BaseFieldDiff

    def test_identical_fields_dict(self):
        """
        The diff between two identical fields of any type should be None.
        """
        vals = ['Lorem', 123, True, datetime.datetime.now()]
        for v in vals:
            d = self.test_class(v, v)
            self.assertEqual(d.as_dict(), None)

    def test_identical_fields_html(self):
        """
        The html of the diff between two identical fields should be a
        sensible message.
        """
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
    def setUp(self):
        self.test_class = TextFieldDiff

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
    def setUp(self):
        self.test_class = FileFieldDiff

    def test_deleted_inserted(self):
        m1 = Diff_M2()
        m1.a.save("a.txt", ContentFile("TEST FILE"), save=False)

        m2 = Diff_M2()
        m2.a.save("b.txt", ContentFile("TEST FILE"), save=False)

        d = self.test_class(m1.a, m2.a).as_dict()
        self.assertTrue(d['deleted'].name == m1.a.name)
        self.assertTrue(d['inserted'].name == m2.a.name)

        m1.a.delete()
        m2.a.delete()


class ImageFieldDiffTest(FileFieldDiffTest):
    def setUp(self):
        self.test_class = ImageFieldDiff


class HtmlFieldTest(TestCase):
    def test_identical_fields(self):
        htmlDiff = HtmlFieldDiff('abc', 'abc')
        self.assertEquals(htmlDiff.as_dict(), None)

    def test_deleted_inserted(self):
        htmlDiff = HtmlFieldDiff('abc', 'def')
        self.assertTrue('def</ins>' in htmlDiff.as_html())

    def test_daisydiff_broken_fallback(self):
        """
        In case something is wrong with the DaisyDiff service, fallback to
        text-only diff
        """
        backup = HtmlFieldDiff.DAISYDIFF_URL

        HtmlFieldDiff.DAISYDIFF_URL = 'http://badurl'
        htmlDiff = HtmlFieldDiff('abc', 'def')
        self.assertTrue('<del>abc</del>' in htmlDiff.as_html())

        HtmlFieldDiff.DAISYDIFF_URL = backup


class GeometryFieldDiffTest(BaseFieldDiffTest):
    def setUp(self):
        self.test_class = GeometryFieldDiff

    def collection_contains_only(self, cls, collection):
        from django.contrib.gis.geos import GeometryCollection
        if type(collection) == cls:
            return True
        for o in collection:
            if isinstance(o, GeometryCollection):
                if not self.collection_contains_only(cls, o):
                    return False
            if type(o) != cls:
                return False
        return True

    def collection_size(self, collection):
        from django.contrib.gis.geos import GeometryCollection
        if not isinstance(collection, GeometryCollection):
            return 1
        i = 0
        for o in collection:
            if isinstance(o, GeometryCollection):
                i += self.collection_size(o)
            else:
                i += 1
        return i

    def test_deleted_inserted(self):
        from django.contrib.gis.geos import GEOSGeometry
        from django.contrib.gis.geos import Polygon, GeometryCollection
        from django.contrib.gis.geos import Point, LineString

        # A polygon.
        a = GEOSGeometry("""{ "type": "GeometryCollection", "geometries": [ { "type": "Polygon", "coordinates": [ [ [ -122.492462, 37.773390 ], [ -122.493664, 37.758327 ], [ -122.476412, 37.758260 ], [ -122.465426, 37.771355 ], [ -122.481734, 37.778953 ], [ -122.492462, 37.773390 ] ] ] } ] }""", srid=4326)
        # Polygon a with a bit added and a bit removed.
        b = GEOSGeometry("""{ "type": "GeometryCollection", "geometries": [ { "type": "Polygon", "coordinates": [ [ [ -122.492462, 37.773390 ], [ -122.493664, 37.758327 ], [ -122.489523, 37.759362 ], [ -122.485038, 37.759854 ], [ -122.476412, 37.758260 ], [ -122.465426, 37.771355 ], [ -122.481734, 37.778953 ], [ -122.485403, 37.779666 ], [ -122.488557, 37.778479 ], [ -122.492462, 37.773390 ] ] ] } ] }""", srid=4326)
        d = self.test_class(a, b).as_dict()
        deleted = d['deleted']
        inserted = d['inserted']

        # Deleted portion should contain a single polygon.
        if type(d['deleted']) == GeometryCollection:
            self.assertEqual(len(d['deleted']), 1)
            deleted = d['deleted'][0]
        if type(d['inserted']) == GeometryCollection:
            self.assertEqual(len(d['inserted']), 1)
            inserted = d['inserted'][0]

        self.assertEqual(type(inserted), Polygon)
        self.assertEqual(type(deleted), Polygon)

        # A bunch of geometries.
        a = GEOSGeometry("""{ "type": "GeometryCollection", "geometries": [ { "type": "Polygon", "coordinates": [ [ [ -122.493149, 37.765401 ], [ -122.492548, 37.761262 ], [ -122.486540, 37.761262 ], [ -122.493149, 37.765401 ] ] ] }, { "type": "MultiPolygon", "coordinates": [ [ [ [ -122.460834, 37.766249 ], [ -122.458087, 37.762585 ], [ -122.462636, 37.759939 ], [ -122.468816, 37.757768 ], [ -122.475168, 37.757157 ], [ -122.461478, 37.761568 ], [ -122.460834, 37.766249 ] ] ], [ [ [ -122.488815, 37.777240 ], [ -122.467185, 37.775748 ], [ -122.467529, 37.760821 ], [ -122.487184, 37.763196 ], [ -122.488815, 37.777240 ] ] ] ] }, { "type": "Point", "coordinates": [ -122.472249, 37.779615 ] }, { "type": "Point", "coordinates": [ -122.482291, 37.779886 ] }, { "type": "Point", "coordinates": [ -122.463495, 37.762925 ] }, { "type": "LineString", "coordinates": [ [ -122.458087, 37.774255 ], [ -122.462550, 37.775477 ], [ -122.464610, 37.772220 ], [ -122.474567, 37.773984 ], [ -122.484866, 37.769506 ], [ -122.497483, 37.769845 ] ] }, { "type": "LineString", "coordinates": [ [ -122.477142, 37.777715 ], [ -122.473966, 37.759803 ] ] }, { "type": "Point", "coordinates": [ -122.464224, 37.777478 ] }, { "type": "Point", "coordinates": [ -122.458302, 37.770897 ] }, { "type": "LineString", "coordinates": [ [ -122.496239, 37.766080 ], [ -122.495896, 37.758005 ], [ -122.482592, 37.758480 ] ] } ] }""", srid=4326)

        # Geometry from a with a point removed, a polygon removed, a
        # line removed, a line added, a point added and a polygon
        # added.
        b = GEOSGeometry("""{ "type": "GeometryCollection", "geometries": [ { "type": "Polygon", "coordinates": [ [ [ -122.461563, 37.770694 ], [ -122.464138, 37.766962 ], [ -122.458044, 37.767165 ], [ -122.461563, 37.770694 ] ] ] }, { "type": "MultiPolygon", "coordinates": [ [ [ [ -122.460834, 37.766249 ], [ -122.458087, 37.762585 ], [ -122.462636, 37.759939 ], [ -122.468816, 37.757768 ], [ -122.475168, 37.757157 ], [ -122.461478, 37.761568 ], [ -122.460834, 37.766249 ] ] ], [ [ [ -122.488815, 37.777240 ], [ -122.467185, 37.775748 ], [ -122.467529, 37.760821 ], [ -122.487184, 37.763196 ], [ -122.488815, 37.777240 ] ] ] ] }, { "type": "Point", "coordinates": [ -122.482291, 37.779886 ] }, { "type": "Point", "coordinates": [ -122.463495, 37.762925 ] }, { "type": "LineString", "coordinates": [ [ -122.477142, 37.777715 ], [ -122.473966, 37.759803 ] ] }, { "type": "Point", "coordinates": [ -122.464224, 37.777478 ] }, { "type": "Point", "coordinates": [ -122.458302, 37.770897 ] }, { "type": "LineString", "coordinates": [ [ -122.496239, 37.766080 ], [ -122.495896, 37.758005 ], [ -122.482592, 37.758480 ] ] }, { "type": "Point", "coordinates": [ -122.491432, 37.775036 ] }, { "type": "LineString", "coordinates": [ [ -122.455469, 37.766758 ], [ -122.455469, 37.760719 ], [ -122.465769, 37.756173 ] ] } ] }""", srid=4326)

        d = self.test_class(a, b).as_dict()
        deleted = d['deleted']
        inserted = d['inserted']

        deleted_polys = [g for g in deleted if type(g) == Polygon]
        inserted_polys = [g for g in inserted if type(g) == Polygon]
        self.assertEqual(len(deleted_polys), 1)
        self.assertEqual(len(inserted_polys), 1)

        deleted_points = [g for g in deleted if type(g) == Point]
        inserted_points = [g for g in inserted if type(g) == Point]
        self.assertEqual(len(deleted_points), 1)
        self.assertEqual(len(inserted_points), 1)

        deleted_lines = [g for g in deleted if type(g) == LineString]
        inserted_lines = [g for g in inserted if type(g) == LineString]
        # We might break up linestrings into lots of linestrings..so
        # it's hard to tell.  Let's just check to make sure it's
        # non-empty for now.
        self.assertTrue(len(deleted_lines) != 0)
        self.assertTrue(len(inserted_lines) != 0)

    def test_line_inserted(self):
        from django.contrib.gis.geos import GEOSGeometry, LineString
        # A polygon.
        a = GEOSGeometry("""{ "type": "GeometryCollection", "geometries": [ { "type": "Polygon", "coordinates": [ [ [ -122.471199, 37.780625 ], [ -122.470169, 37.724435 ], [ -122.393264, 37.725793 ], [ -122.398071, 37.781711 ], [ -122.471199, 37.780625 ] ] ] } ] }""", srid=4326)
        # Polygon from a with a line through it.
        b = GEOSGeometry("""{ "type": "GeometryCollection", "geometries": [ { "type": "Polygon", "coordinates": [ [ [ -122.471199, 37.780625 ], [ -122.470169, 37.724435 ], [ -122.393264, 37.725793 ], [ -122.398071, 37.781711 ], [ -122.471199, 37.780625 ] ] ] }, { "type": "LineString", "coordinates": [ [ -122.487163, 37.770992 ], [ -122.364597, 37.731902 ] ] } ] }""", srid=4326)

        d = self.test_class(a, b).as_dict()

        # The diff should contain a *single* line segment.
        self.assertTrue(self.collection_contains_only(LineString, d['inserted']))
        self.assertEqual(self.collection_size(d['inserted']), 1)

    def test_collection_handling(self):
        from django.contrib.gis.geos import GEOSGeometry, Point
        # A collection with three points.
        a = GEOSGeometry("""GEOMETRYCOLLECTION (POINT (-122.4171253967300004 37.8168416846629967), POINT (-122.5226971435500047 37.7849668879050000), POINT (-122.4329182433999961 37.7185961029840016))""")
        # Collection A with a point moved.
        b = GEOSGeometry("""GEOMETRYCOLLECTION (POINT (-122.4171253967300004 37.8168416846629967), POINT (-122.4749752807600061 37.7958194267970029), POINT (-122.4329182433999961 37.7185961029840016))""")

        d = self.test_class(a, b).as_dict()

        # The diff should have one point added, one point deleted, one
        # point the same.
        self.assertTrue(self.collection_contains_only(Point, d['inserted']))
        self.assertEqual(self.collection_size(d['inserted']), 1)
        self.assertTrue(self.collection_contains_only(Point, d['deleted']))
        self.assertEqual(self.collection_size(d['deleted']), 1)
        self.assertTrue(self.collection_contains_only(Point, d['same']))
        self.assertEqual(self.collection_size(d['same']), 2)


class DiffRegistryTest(TestCase):
    def setUp(self):
        self.registry = Registry()

        vals = {'a': 'Lorem', 'b': 'Ipsum',
                'c': datetime.datetime.now(), 'd': 123}
        m1 = Diff_M1.objects.create(**vals)

    def test_can_handle_any_field(self):
        """
        Out of the box, the registry should offer diff utils for any field.
        """
        r = self.registry
        field_types = [db.models.CharField, db.models.TextField,
                       db.models.BooleanField]
        for t in field_types:
            d = r.get_diff_util(t)
            self.assertTrue(issubclass(d, BaseFieldDiff))

    def test_can_handle_any_model(self):
        """
        Out of the box, the registry should offer diff utils for any model.
        """
        r = self.registry
        for t in TEST_MODELS:
            d = r.get_diff_util(t)
            self.assertTrue(issubclass(d, BaseModelDiff))

    def test_fallback_diff(self):
        class AwesomeImageField(db.models.ImageField):
            pass
        """
        If we don't have a diff util for the exact field type, we should fall
        back to the diff util for the base class, until we find a registered
        util.
        """
        self.registry.register(db.models.FileField, FileFieldDiff)
        d = self.registry.get_diff_util(AwesomeImageField)
        self.assertTrue(issubclass(d, FileFieldDiff))

    def test_register_model(self):
        """
        If we register a diff for a model, we should get that and not
        BaseModelDiff.
        """
        self.registry.register(Diff_M1, Diff_M1Diff)
        self.failUnlessEqual(self.registry.get_diff_util(Diff_M1), Diff_M1Diff)

    def test_register_field(self):
        """
        If we register a fielddiff for a model, we should get that and not
        BaseFieldDiff.
        """
        self.registry.register(db.models.CharField, Diff_M1FieldDiff)
        self.failUnlessEqual(self.registry.get_diff_util(db.models.CharField),
                             Diff_M1FieldDiff)

    def test_cannot_diff_something_random(self):
        """
        If we try to diff something that is neither a model nor a field,
        raise exception.
        """
        self.failUnlessRaises(diff.diffutils.DiffUtilNotFound,
                              self.registry.get_diff_util, DiffRegistryTest)
