import httplib
import urlparse
import html5lib
import lxml

from django.conf import settings
from django.utils.http import urlencode
from lxml import etree

DAISYDIFF_URL = getattr(settings, 'DAISYDIFF_URL',
    'http://localhost:8080/diff')
DAISYDIFF_MERGE_URL = getattr(settings, 'DAISYDIFF_MERGE_URL',
    'http://localhost:8080/merge')


class ServiceUnavailableError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def daisydiff(field1, field2, service_url=DAISYDIFF_URL):
    """
    Gets the HTML diff from the DaisyDiff server and returns it
    as a table row
    """
    params = urlencode({'field1': field1, 'field2': field2})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/html"}
    split_url = urlparse.urlsplit(service_url)

    conn = httplib.HTTPConnection(split_url.netloc)
    conn.request("POST", split_url.path, params, headers)
    response = conn.getresponse()
    if not response.status == 200:
        raise ServiceUnavailableError("Service responded with status %i %s"
                                      % (response.status, response.reason))
    data = response.read()
    conn.close()
    row = extract_table_row(data)
    row.attributes['class'] = 'htmldiff'
    return row.toxml()


def daisydiff_merge(field1, field2, ancestor, service_url=DAISYDIFF_MERGE_URL):
    """
    Uses the DaisyDiff server to merge the two versions of the field, given a
    common ancestor and returns the tuple (merged_version, has_conflict) where
    has_conflict is True if the merge could not be done cleanly.
    """
    params = urlencode({'field1': field1, 'field2': field2,
                        'ancestor': ancestor})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/html"}
    split_url = urlparse.urlsplit(service_url)

    conn = httplib.HTTPConnection(split_url.netloc)
    conn.request("POST", split_url.path, params, headers)
    response = conn.getresponse()
    if not response.status == 200:
        raise ServiceUnavailableError("Service responded with status %i %s"
                                      % (response.status, response.reason))
    data = response.read()
    conn.close()
    return extract_merge(data)


def extract_merge(xml):
    doc = lxml.etree.fromstring(xml)
    # remove repeating conflict messages
    last_conflict_message = None
    tree = etree.iterwalk(doc)
    for action, elem in tree:
        if elem.tag == 'strong' and elem.attrib.get('class') == 'editConflict':
            if elem.text == last_conflict_message:
                elem.getparent().remove(elem)
            last_conflict_message = elem.text
    body_list = [lxml.etree.tostring(child, method='html', encoding='UTF-8')
                                 for child in doc.find('body')]
    body = ''.join(body_list)
    has_conflict = 'true' in doc.find('conflict').text
    return (body, has_conflict)


def extract_table_row(html):
    doc = html5lib.parse(html)
    return find_element_by_tag('tr', doc)


def find_element_by_tag(tag, node):
    """
    Depth-first search for first element with the given tag
    """
    for c in node.childNodes:
        if c.name == tag:
            return c
        el = find_element_by_tag(tag, c)
        if not el is None:
            return el
    return None
