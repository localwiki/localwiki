from django.test import TestCase

from pages.models import Page
from regions.models import Region

from .. models import Redirect
from .. import exceptions


class RedirectTest(TestCase):
    def setUp(self):
        self.region = Region(full_name="Test Region", slug="test_region")
        self.region.save()

    def test_redirect_to_self(self):
        p = Page(name="foobar", content="<p>foobar</p>", region=self.region)
        p.save()
        r = Redirect(source='foobar', destination=p, region=self.region)
        self.assertRaises(exceptions.RedirectToSelf, r.save)
