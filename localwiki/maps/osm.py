from subprocess import Popen, PIPE, STDOUT
from urlparse import urljoin
from lxml import etree
import csv
import os
from cStringIO import StringIO

import requests

from django.contrib.gis.geos import GEOSGeometry, GeometryCollection

OSM_OVERPASS_API = 'http://overpass-api.de/api/interpreter'
OSM_REVERSE_GEOCODE_API = 'http://nominatim.openstreetmap.org/reverse'

def approx_km_to_degree(km):
    return (km / 40000.0) * 360 

def get_item_name(osm_id, osm_type, display_name):
    return display_name.split(',')[0]
    # The commented-out code below gets the exact name value by doing another
    # lookup to the OSM Overpass API.  This is unfortunately quite slow.
    # So what we do is guess the name based on the provided display_name.
    # If this display name trick stops working then we can:
    #   1) Find another heuristic to get the exact name value.
    #   2) Use a different OSM API to get the name value - the Overpass
    #      API is in Germany and is kind of slow.  There may be a simpler
    #      API that's closer / faster.

    #r = requests.post(OSM_OVERPASS_API, data=
    #    """<osm-script><id-query ref="%s" type="%s"/><print/></osm-script>""" % (osm_id, osm_type)
    #)
    #root = etree.fromstring(r.text.encode('utf-8'))
    #return root.find('.//tag[@k="name"]').attrib['v']

def get_osm_xml(osm_id, osm_type, display_name, region):
    name = get_item_name(osm_id, osm_type, display_name)
    # Buffer the region by about 8km to get nearby objects.
    radius = approx_km_to_degree(8)
    extent = region.geom.buffer(radius).envelope.coords[0]
    n, e, s, w = (extent[2][1], extent[2][0], extent[0][1], extent[0][0])
    recursive_find_with_bbox = """
<query type="%(type)s">
  <has-kv k="name" v="%(name)s"/>
  <bbox-query n="%(n)s" e="%(e)s" s="%(s)s" w="%(w)s"/>
</query>
<union>
  <item/>
  <recurse type="down"/>
</union>
<print/>
    """ % {
        'name': name,
        'type': osm_type,
        'n': n,
        'e': e,
        's': s,
        'w': w,
    }
    r = requests.post(OSM_OVERPASS_API, data=recursive_find_with_bbox)
    return r.text

def xml_to_geom(layer, osm_xml):
    os.environ['OSM_USE_CUSTOM_INDEXING'] = 'NO'
    p = Popen(['ogr2ogr', '-f', 'CSV', '/vsistdout/', '/vsistdin/', layer, '-lco', 'GEOMETRY=AS_WKT' ], stdout=PIPE, stdin=PIPE, stderr=PIPE, env=os.environ)
    output = p.communicate(input=osm_xml)[0]
    reader = csv.reader(StringIO(output))
    try:
        reader.next()
        wkts = [r[0] for r in reader]
        return [GEOSGeometry(wkt) for wkt in wkts]
    except:
        return None

def get_osm_geom(osm_id, osm_type, display_name, region):
    osm_xml = get_osm_xml(osm_id, osm_type, display_name, region)
    geoms = []

    # We don't care about points for ways.
    if osm_type != 'way':
        points = xml_to_geom('points', osm_xml)
        if points:
            geoms += points
    lines = xml_to_geom('lines', osm_xml)
    if lines:
        geoms += lines
    multilinestrings = xml_to_geom('multilinestrings', osm_xml)
    if multilinestrings:
        geoms += multilinestrings
    multipolygons = xml_to_geom('multipolygons', osm_xml)
    if multipolygons:
        geoms += multipolygons
    other_relations = xml_to_geom('other_relations', osm_xml)
    if other_relations:
        geoms += other_relations

    return GeometryCollection(geoms)
