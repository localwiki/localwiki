from subprocess import Popen, PIPE, STDOUT
from urlparse import urljoin
import csv
import os
from cStringIO import StringIO

import requests

from django.contrib.gis.geos import GEOSGeometry, GeometryCollection

OSM_API = 'http://api.openstreetmap.org/api/0.6/'

def get_osm_xml(osm_id, osm_type):
    r = requests.get(urljoin(OSM_API, '%s/%s/full' % (osm_type, osm_id)))
    return r.text

def xml_to_geom(layer, osm_xml):
    os.environ['OSM_USE_CUSTOM_INDEXING'] = 'NO'
    p = Popen(['ogr2ogr', '-f', 'CSV', '/vsistdout/', '/vsistdin/', layer, '-lco', 'GEOMETRY=AS_WKT' ], stdout=PIPE, stdin=PIPE, stderr=PIPE, env=os.environ)
    output = p.communicate(input=osm_xml)[0]
    reader = csv.reader(StringIO(output))
    try:
        reader.next()
        wkt = reader.next()[0]
        return GEOSGeometry(wkt)
    except:
        return None

def get_osm_geom(osm_id, osm_type):
    osm_xml = get_osm_xml(osm_id, osm_type)

    geoms = []
    points = xml_to_geom('points', osm_xml)
    if points:
        geoms.append(points)
    lines = xml_to_geom('lines', osm_xml)
    if lines:
        geoms.append(lines)
    multilinestrings = xml_to_geom('multilinestrings', osm_xml)
    if multilinestrings:
        geoms.append(multilinestrings)
    multipolygons = xml_to_geom('multipolygons', osm_xml)
    if multipolygons:
        geoms.append(multipolygons)
    other_relations = xml_to_geom('other_relations', osm_xml)
    if other_relations:
        geoms.append(other_relations)
    
    return GeometryCollection(geoms)
