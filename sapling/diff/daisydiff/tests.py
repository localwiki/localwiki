from django.test import TestCase
from django.conf import settings
from daisydiff import daisydiff
import socket

TEST_SERVICE = hasattr(settings, 'DAISYDIFF_URL')

def skipUnlessHasService(test):
    def do_nothing(*args, **kwargs):
        print "Skipping %r (DAISYDIFF_URL not in settings.py)" % test.__name__
    if not TEST_SERVICE:
        return do_nothing
    return test

class DaisyDiffTest(TestCase):
    def test_bad_url_throws_exception(self):
        self.assertRaises(socket.error, daisydiff, 'abc', 'abc', 'badurl')
        print 
    
    def url_set(self):
        return hasattr(settings, 'DAISYDIFF_URL')
    
    @skipUnlessHasService
    def test_server_is_running(self):        
        import httplib
        import urlparse
        split_url = urlparse.urlsplit(settings.DAISYDIFF_URL)
        conn = httplib.HTTPConnection(split_url.netloc)
        conn.request("GET", split_url.path)
        r1 = conn.getresponse()
        self.assertEquals(r1.status, 200)
        
    @skipUnlessHasService
    def test_daisydiff_service(self):
        tr = daisydiff('abc', 'def')
        self.failUnless('abc</del>' in tr)
        self.failUnless('def</ins>' in tr)
            