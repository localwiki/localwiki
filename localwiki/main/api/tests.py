import json

from django.contrib.auth.models import User, Group
from django.conf import settings

from rest_framework import status
from rest_framework.authtoken.models import Token

from regions.models import Region
from pages.models import Page

from .test import APITestCase


class AuthenticationAPITests(APITestCase):
    def setUp(self):
        super(AuthenticationAPITests, self).setUp()

        # Create the edit user and add it to the authenticated group
        self.edit_user = User(
            username="edituser", email="edituser@example.org", password="fakepassword")
        self.edit_user.save()
        all_group, created = Group.objects.get_or_create(name=settings.USERS_DEFAULT_GROUP)
        self.edit_user.groups.add(all_group)
        self.edit_user.save()

        # Create auth token for the edit user
        self.token = Token.objects.get_or_create(user=self.edit_user)[0]

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

    def test_basic_page_post(self):
        # Without authentication, a POST should fail
        data = {'name': 'Test Page', 'content': '<p>hi</p>', 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf_region.id)}
        resp = self.client.post('%s/pages/' % self.API_ROOT, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # Now try with an API token, which should work
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {'name': 'Test Page', 'content': '<p>hi</p>', 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf_region.id)}
        resp = self.client.post('%s/pages/' % self.API_ROOT, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Now check to make sure the page version was edited by the user associated with the API token
        p = Page.objects.get(region=self.sf_region, name="Test Page")
        self.assertEqual(p.versions.most_recent().version_info.user, self.edit_user)
