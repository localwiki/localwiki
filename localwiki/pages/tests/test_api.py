import json

from rest_framework.test import APITestCase
from rest_framework import status

from regions.models import Region

from .. models import Page


class PageAPITests(APITestCase):
    def setUp(self):
        self.sf_region = Region(full_name='San Francisco', slug='sf')
        self.sf_region.save()

        p = Page(region=self.sf_region)
        p.content = '<p>Dolores Park here</p>'
        p.name = 'Dolores Park'
        p.save()
        self.dolores_park = p

        p = Page(region=self.sf_region)
        p.content = '<p>Duboce Park here</p>'
        p.name = 'Duboce Park'
        p.save()
        self.duboce_park = p

    def test_basic_page_list(self):
        response = self.client.get('/api/pages/')
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 2)

    def test_basic_page_detail(self):
        response = self.client.get('/api/pages/?slug=dolores%20park')
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)
        self.assertEqual(jresp['results'][0]['name'], 'Dolores Park')

    def test_basic_page_post(self):
        # Without authentication, a POST should fail
        data = {'name': 'Test Page', 'content': '<p>hi</p>', 'region': 'http://testserver/api/regions/%s/' % (self.sf_region.id)}
        resp = self.client.post('/api/pages/', data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
