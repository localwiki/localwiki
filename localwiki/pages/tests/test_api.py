import json

from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db import IntegrityError

from rest_framework import status
from rest_framework.authtoken.models import Token

from main.api.test import APITestCase
from regions.models import Region
from redirects.models import Redirect
from tags.models import Tag, PageTagSet

from .. models import Page


class PageAPITests(APITestCase):
    def setUp(self):
        super(PageAPITests, self).setUp()

        # Create the edit user and add it to the authenticated group
        self.edit_user = User(
            username="edituser", email="edituser@example.org", password="fakepassword")
        self.edit_user.save()
        all_group, created = Group.objects.get_or_create(name=settings.USERS_DEFAULT_GROUP)
        self.edit_user.groups.add(all_group)
        self.edit_user.save()

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

        t1 = Tag(name='lake')
        t1.save()
        t2 = Tag(name='water')
        t2.save()
        pts = PageTagSet(page=p, region=self.sf_region)
        pts.save()
        pts.tags = [t1, t2]
        
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
        self.client.force_authenticate(user=self.edit_user)

        data = {'name': 'Test Page', 'content': '<p>hi</p>', 'region': 'http://testserver/api/regions/%s/' % (self.sf_region.id)}
        resp = self.client.post('/api/pages/', data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_page_post_with_tags(self):
        self.client.force_authenticate(user=self.edit_user)

        data = {'name': 'Test Page with tags', 'content': '<p>hi with tags</p>',
                'tags': ['park', 'fun'],
                'region': 'http://testserver/api/regions/%s/' % (self.sf_region.id)}
        resp = self.client.post('/api/pages/', data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        jresp = json.loads(resp.content)
        self.assertEqual(set(jresp['tags']), set(['park', 'fun']))

    def test_post_no_region(self):
        self.client.force_authenticate(user=self.edit_user)

        data = {'name': 'Test Page no region', 'content': '<p>hi with tags</p>'}
        resp = self.client.post('/api/pages/', data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_tags(self):
        response = self.client.get('/api/pages/?tags=lake')
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)
        self.assertEqual(jresp['results'][0]['slug'], 'duboce park')

        response = self.client.get('/api/pages/?tags=lake,wifi')
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 0)

        response = self.client.get('/api/pages/?tags=water,lake')
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)

    def test_post_page_already_exists(self):
        self.client.force_authenticate(user=self.edit_user)

        data = {'slug': 'dolores park', 'name': 'Dolores Park', 'content': '<p>hi exists</p>', 'region': 'http://testserver/api/regions/%s/' % (self.sf_region.id)}
        try:
            resp = self.client.post('/api/pages/', data, format='json')
        except IntegrityError:
            pass
        else:
            self.assertTrue(False)

    def test_filter_slug(self):
        response = self.client.get('/api/pages/?slug__icontains=PaRk')
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 2)

        response = self.client.get('/api/pages/?slug__istartswith=DOLO')
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)
        self.assertEqual(jresp['results'][0]['slug'], 'dolores park')

    def test_basic_page_put(self):
        self.client.force_authenticate(user=self.edit_user)

        data = {'name': 'Duboce Park', 'content': '<p>hi new content</p>', 'region': 'http://testserver/api/regions/%s/' % (self.sf_region.id)}
        resp = self.client.put('/api/pages/%s/' % self.duboce_park.id, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        jresp = json.loads(resp.content)

        # Make sure the tags are still there even though we didn't update them.
        self.assertEqual(jresp['content'], '<p>hi new content</p>')
        self.assertEqual(set(jresp['tags']), set(['lake', 'water']))

    def test_basic_page_patch(self):
        self.client.force_authenticate(user=self.edit_user)

        data = {'name': 'Duboce PARK'}
        resp = self.client.patch('/api/pages/%s/' % self.duboce_park.id, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        jresp = json.loads(resp.content)

        self.assertEqual(jresp['content'], '<p>Duboce Park here</p>')
        self.assertEqual(jresp['name'], 'Duboce PARK')

    def test_change_page_name(self):
        self.client.force_authenticate(user=self.edit_user)

        data = {'name': 'Duboce Cat'}
        resp = self.client.patch('/api/pages/%s/' % self.duboce_park.id, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        jresp = json.loads(resp.content)

        self.assertEqual(jresp['content'], '<p>Duboce Park here</p>')
        self.assertEqual(jresp['name'], 'Duboce Cat')

        # Redirect should exist, as the page should have been renamed
        self.assertTrue(Redirect.objects.filter(source='duboce park').exists())
        redirect = Redirect.objects.get(source='duboce park')
        self.assertEqual(redirect.destination, Page.objects.get(slug='duboce cat'))
