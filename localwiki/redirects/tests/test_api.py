import json

from rest_framework import status

from django.contrib.auth.models import User, Group
from django.conf import settings

from main.api.test import APITestCase
from regions.models import Region
from pages.models import Page

from .. models import Redirect


class RedirectAPITests(APITestCase):
    def setUp(self):
        super(RedirectAPITests, self).setUp()

        # Create the edit user and add it to the authenticated group
        self.edit_user = User(
            username="edituser", email="edituser@example.org", password="fakepassword")
        self.edit_user.save()
        all_group, created = Group.objects.get_or_create(name=settings.USERS_DEFAULT_GROUP)
        self.edit_user.groups.add(all_group)
        self.edit_user.save()

        self.sf = Region(full_name="San Francisco", slug="sf")
        self.sf.save()
        self.oak = Region(full_name="Oakland", slug="oak")
        self.oak.save()

        self.dolores_park = Page(name="Dolores Park", content="<p>Hi</p>", region=self.sf)
        self.dolores_park.save()

        self.duboce_park = Page(name="Duboce Park", content="<p>Hi</p>", region=self.sf)
        self.duboce_park.save()

        self.mission_dolores_park = Redirect(
            source="mission dolores park",
            destination=self.dolores_park,
            region=self.sf
        )
        self.mission_dolores_park.save()

        self.dog_park = Redirect(
            source="dog park",
            destination=self.duboce_park,
            region=self.sf
        )
        self.dog_park.save()

    def test_redirect_list(self):
        response = self.client.get('/api/redirects/')
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 2)

    def test_redirect_simple_post(self):
        self.client.force_authenticate(user=self.edit_user)

        data = {'source': 'redirect from pg', 'destination': 'http://testserver/api/pages/%s/' % (self.dolores_park.id), 'region': 'http://testserver/api/regions/%s/' % (self.sf.id)}
        resp = self.client.post('/api/redirects/', data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_destination_chained_filter(self):
        response = self.client.get('/api/redirects/?destination__slug__icontains=dolores')
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)
