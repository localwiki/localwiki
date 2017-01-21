from django.test import TestCase

from pages.models import Page

from models import Redirect
import exceptions


class RedirectTest(TestCase):
    def test_redirect_to_self(self):
        p = Page(name="foobar", content="<p>foobar</p>")
        p.save()
        r = Redirect(source='foobar', destination=p)
        self.assertRaises(exceptions.RedirectToSelf, r.save)
