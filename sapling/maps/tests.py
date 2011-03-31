from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry

from fields import *


class FlatGeometryCollectionTest(TestCase):
    def test_flatten(self):
        # A geometry collection with a bunch of stuff inside of a
        # rectangle.  And a few items outside of it.
        geom = GEOSGeometry("""{ "type": "GeometryCollection", "geometries": [ { "type": "Polygon", "coordinates": [ [ [ -122.443056, 37.787064 ], [ -122.443056, 37.758434 ], [ -122.400999, 37.757891 ], [ -122.403402, 37.787742 ], [ -122.443056, 37.787064 ] ] ] }, { "type": "Point", "coordinates": [ -122.434816, 37.784758 ] }, { "type": "Point", "coordinates": [ -122.410612, 37.781909 ] }, { "type": "Point", "coordinates": [ -122.432241, 37.766983 ] }, { "type": "Point", "coordinates": [ -122.409754, 37.768747 ] }, { "type": "LineString", "coordinates": [ [ -122.415075, 37.784351 ], [ -122.425890, 37.765083 ], [ -122.427435, 37.779466 ] ] }, { "type": "Polygon", "coordinates": [ [ [ -122.438765, 37.778788 ], [ -122.439966, 37.763726 ], [ -122.457132, 37.772139 ], [ -122.438765, 37.778788 ] ] ] }, { "type": "Point", "coordinates": [ -122.415762, 37.792762 ] }, { "type": "Point", "coordinates": [ -122.430696, 37.791541 ] }, { "type": "LineString", "coordinates": [ [ -122.397394, 37.790727 ], [ -122.395849, 37.754498 ], [ -122.448549, 37.761962 ] ] } ] }""", srid=4326)
        # A geometry collection with nothing inside the rectangle and a
        # few items outside of it.
        expected_geom = GEOSGeometry("""{ "type": "GeometryCollection", "geometries": [ { "type": "Polygon", "coordinates": [ [ [ -122.443056, 37.765240 ], [ -122.457132, 37.772139 ], [ -122.443056, 37.777235 ], [ -122.443056, 37.787064 ], [ -122.403402, 37.787742 ], [ -122.400999, 37.757891 ], [ -122.443056, 37.758434 ], [ -122.443056, 37.765240 ] ] ] }, { "type": "Point", "coordinates": [ -122.415762, 37.792762 ] }, { "type": "Point", "coordinates": [ -122.430696, 37.791541 ] }, { "type": "LineString", "coordinates": [ [ -122.397394, 37.790727 ], [ -122.395849, 37.754498 ], [ -122.448549, 37.761962 ] ] } ] }""", srid=4326)
        field = FlatGeometryCollectionField()
        self.assertTrue(field._flatten(geom).equals_exact(expected_geom, 0.001))

        # A point, a line and a triangle, none overlapping.
        geom = GEOSGeometry("""{ "type": "GeometryCollection", "geometries": [ { "type": "Point", "coordinates": [ -122.435760, 37.786250 ] }, { "type": "LineString", "coordinates": [ [ -122.428036, 37.784215 ], [ -122.399883, 37.782180 ] ] }, { "type": "Polygon", "coordinates": [ [ [ -122.441597, 37.774853 ], [ -122.442627, 37.755855 ], [ -122.404861, 37.763048 ], [ -122.441597, 37.774853 ] ] ] } ] }""", srid=4326)
        field = FlatGeometryCollectionField()
        # Should stay the same.
        self.assertTrue(field._flatten(geom).equals(geom))

        # Two triangles, both containing a triangle and with an
        # overlapping triangle.
        geom = GEOSGeometry("""{ "type": "GeometryCollection", "geometries": [ { "type": "Polygon", "coordinates": [ [ [ -122.445459, 37.761555 ], [ -122.404604, 37.753955 ], [ -122.415075, 37.789099 ], [ -122.445459, 37.761555 ] ] ] }, { "type": "Polygon", "coordinates": [ [ [ -122.456617, 37.785707 ], [ -122.448549, 37.775667 ], [ -122.437220, 37.787878 ], [ -122.456617, 37.785707 ] ] ] }, { "type": "Polygon", "coordinates": [ [ [ -122.451296, 37.784351 ], [ -122.448549, 37.778788 ], [ -122.443399, 37.785165 ], [ -122.451296, 37.784351 ] ] ] }, { "type": "Polygon", "coordinates": [ [ [ -122.418852, 37.777160 ], [ -122.434816, 37.764676 ], [ -122.411642, 37.759926 ], [ -122.418852, 37.777160 ] ] ] }, { "type": "Polygon", "coordinates": [ [ [ -122.409582, 37.783265 ], [ -122.422113, 37.774311 ], [ -122.399454, 37.774582 ], [ -122.409582, 37.783265 ] ] ] }, { "type": "Polygon", "coordinates": [ [ [ -122.449751, 37.790727 ], [ -122.447348, 37.783265 ], [ -122.440310, 37.792219 ], [ -122.449751, 37.790727 ] ] ] } ] }""", srid=4326)
        # Two polygons.
        expected_geom = GEOSGeometry("""{ "type": "GeometryCollection", "geometries": [ { "type": "MultiPolygon", "coordinates": [ [ [ [ -122.410710, 37.774447 ], [ -122.404604, 37.753955 ], [ -122.445459, 37.761555 ], [ -122.415075, 37.789099 ], [ -122.412678, 37.781053 ], [ -122.409582, 37.783265 ], [ -122.399454, 37.774582 ], [ -122.410710, 37.774447 ] ] ], [ [ [ -122.444349, 37.787080 ], [ -122.437220, 37.787878 ], [ -122.448549, 37.775667 ], [ -122.456617, 37.785707 ], [ -122.448429, 37.786624 ], [ -122.449751, 37.790727 ], [ -122.440310, 37.792219 ], [ -122.444349, 37.787080 ] ] ] ] } ] }""", srid=4326)
        self.assertTrue(field._flatten(geom).equals_exact(expected_geom, 0.001))
