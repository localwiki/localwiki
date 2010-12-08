import httplib
import urllib
import urlparse
import html5lib

from django.conf import settings

DAISYDIFF_URL = getattr(settings, 'DAISYDIFF_URL', 'http://localhost:8080')

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
    params = urllib.urlencode({'field1': field1, 'field2': field2})
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
    return extract_table_row(data)
    
def extract_table_row(html):
    doc = html5lib.parse(html)
    return find_element_by_tag('tr', doc).toxml()

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