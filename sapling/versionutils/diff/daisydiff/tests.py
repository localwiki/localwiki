from django.test import TestCase
from django.conf import settings
from daisydiff import daisydiff
import socket
from versionutils.diff.daisydiff.daisydiff import daisydiff_merge

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

    @skipUnlessHasService
    def test_nbsp(self):
        tr = daisydiff(u'Hello \xa0 World', u'Hello World')
        self.assertEquals(tr,
             (u'<tr class="htmldiff">\n<td>Hello <del class="diff-html-removed'
              u'">\xa0 </del>World</td><td>Hello World</td>\n</tr>'))


class DaisyDiffMergeTest(TestCase):
    def test_bad_url_throws_exception(self):
        self.assertRaises(socket.error, daisydiff_merge,
            'abc', 'abc', 'abc', 'badurl')

    @skipUnlessHasService
    def test_merge_clean(self):
        (body, conflict) = daisydiff_merge(
            '<p>New stuff before</p><p>Original</p>',
            '<p>Original</p><p>New stuff after</p>',
            '<p>Original</p>'
        )
        self.failUnless(conflict is False)
        self.failUnless('New stuff before' in body)
        self.failUnless('Original' in body)
        self.failUnless('New stuff after' in body)

    @skipUnlessHasService
    def test_poor_quality_merge_style(self):
        """
        This doesn't quite work right but at least shouldn't lose anything.
        """
        (body, conflict) = daisydiff_merge(
            '<p><strong>Original</strong></p>',
            '<p><strong>Original</strong></p><p>New stuff</p>',
            '<p>Original</p>'
        )
        self.failUnless(conflict is False)
        self.failUnlessEqual(body,
                            '<p>Original</p><p>New stuff</p>')

    @skipUnlessHasService
    def test_merge_conflict(self):
        (body, conflict) = daisydiff_merge(
            '<p>First version</p>',
            '<p>Second version</p>',
            '<p>Original</p>'
        )
        self.failUnless(conflict is True)
        self.failUnless('Edit conflict' in body)
        self.failUnless('First version' in body)
        self.failUnless('Second version' in body)
        self.failUnless('Original' not in body)

    ##################################################################
    # These tests are probably a bit too strict, but it's better than
    # nothing for now.
    ##################################################################
    @skipUnlessHasService
    def test_merge_conflict_is_readable(self):
        ancestor = ('<p>Rosamunde sells delicious gourmet sausages!</p>'
                    '<p>Vegans and beer-lovers are invited!</p>')
        mine = ('<p>Rosamunde sells delicious gourmet sausages!</p>'
                '<p>Vegans and beer-lovers are invited!</p>'
                '<p>Their "mission street" sausage is a $6.50 play on the '
                'classic <a href="/Bacon-wrapped_hot_dogs">bacon wrapped hot '
                'dog</a>.</p>')
        theirs = ('<p>Rosamunde sells delicious gourmet sausages!</p>'
                  '<p>Vegans and beer-lovers are invited!</p>'
                  '<p><a href="http://rosamundesausagegrill.com/haight-street"'
                  '>Menu</a> (Haight Street)</p>'
                  '<p><a href="http://rosamundesausagegrill.com/mission-street'
                  '">Menu</a> (Mission Street)</p>')
        (body, conflict) = daisydiff_merge(mine, theirs, ancestor)

        expected = ('<p>Rosamunde sells delicious gourmet sausages!</p>'
                '<p>Vegans and beer-lovers are invited!</p>'
                '<strong class="editConflict">Edit conflict! Other version:'
                '</strong>'
                '<p><a href="http://rosamundesausagegrill.com/haight-street">'
                'Menu</a> (Haight Street)</p><p>'
                '<a href="http://rosamundesausagegrill.com/mission-street"'
                '>Menu</a> (Mission Street)</p>'
                '<strong class="editConflict">Edit conflict! Your version:'
                '</strong>'
                '<p>Their "mission street" sausage is a $6.50 play on the '
                'classic <a href="/Bacon-wrapped_hot_dogs">bacon wrapped hot '
                'dog</a>.</p>')

        self.failUnless(conflict is True)
        self.failUnlessEqual(body, expected)

