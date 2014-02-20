import json

from rest_framework import status

from main.api.test import APITestCase
from ..models import Region


class RegionAPITests(APITestCase):
    def setUp(self):
        self.regions = []

        self.sf = Region(full_name="San Francisco", slug="sf")
        self.sf.save()
        self.oak = Region(full_name="Oakland", slug="oak")
        self.oak.save()

    def test_region_list(self):
        response = self.client.get('%s/regions/' % self.API_ROOT)
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 2)

    def test_region_detail(self):
        response = self.client.get('%s/regions/?slug=sf' % self.API_ROOT)
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)
        self.assertEqual(jresp['results'][0]['full_name'], 'San Francisco')
