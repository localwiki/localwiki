import json

from rest_framework import status
from guardian.shortcuts import assign_perm, remove_perm

from django.contrib.auth.models import User, Group
from django.conf import settings

from main.api.test import APITestCase
from regions.models import Region, BannedFromRegion
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

        self.edit_user_2 = User(
            username="edituser2", email="edituser2@example.org", password="fakepassword")
        self.edit_user_2.save()
        all_group, created = Group.objects.get_or_create(name=settings.USERS_DEFAULT_GROUP)
        self.edit_user_2.groups.add(all_group)
        self.edit_user_2.save()

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
        response = self.client.get('%s/redirects/' % self.API_ROOT)
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 2)

    def test_redirect_simple_post(self):
        self.client.force_authenticate(user=self.edit_user)

        data = {'source': 'redirect from pg', 'destination': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.dolores_park.id), 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.post('%s/redirects/' % self.API_ROOT, data, format='json')
        jresp = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(jresp['source'], 'redirect from pg')

    def test_redirect_destination_noexist(self):
        self.client.force_authenticate(user=self.edit_user)

        data = {'source': 'redirect from pg', 'destination': 'http://testserver%s/pages/3585484585/' % self.API_ROOT, 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.post('%s/redirects/' % self.API_ROOT, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destination_chained_filter(self):
        response = self.client.get('%s/redirects/?destination__slug__icontains=dolores' % self.API_ROOT)
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)

    def test_redirect_permissions(self):
        self.client.force_authenticate(user=self.edit_user)

        # We want to tie the redirect permissions should be tied to the
        # Redirect object -and- the Page object that's associated with the
        # redirect.   This is so that if, for instance, Page(name="Front Page")
        # is only editable by a certain group, creating a Redirect from
        # "Front Page" to somewhere is similarly protected.

        #####################################################################################
        # 1. Redirect already exists, redirects.change_redirect / redirects.delete_redirect
        #    should be checked.
        #####################################################################################

        # Make it so only edit_user_2 can edit the Mission Dolores Park redirect 
        assign_perm('change_redirect', self.edit_user_2, self.mission_dolores_park)

        # Now try and update the "Mission Dolores Park" redirect as edit_user

        data = {'source': 'mission dolores park', 'destination': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.duboce_park.id), 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/redirects/%s/' % (self.API_ROOT, self.mission_dolores_park.id), data, format='json')
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Now remove the permission and it should work
        remove_perm('change_redirect', self.edit_user_2, self.mission_dolores_park)

        data = {'source': 'mission dolores park', 'destination': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.duboce_park.id), 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/redirects/%s/' % (self.API_ROOT, self.mission_dolores_park.id), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        #####################################################################################
        # 2. Redirect doesn't exist yet but a `source` page does.
        #    pages.change_page should be checked.
        #####################################################################################

        # Let's create a page
        p = Page(
            name="Oasis",
            content="<p>Blah</p>",
            region=self.sf
        )
        p.save()

        # and then set permissions to restrict it from being edited by `edit_user`
        assign_perm('change_page', self.edit_user_2, p)

        # now let's try and create a redirect from "oasis" to "duboce park" as `edit_user`:

        data = {'source': 'oasis', 'destination': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.duboce_park.id), 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.post('%s/redirects/' % self.API_ROOT, data, format='json')
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Now remove the permission and it should work
        remove_perm('change_page', self.edit_user_2, p)

        data = {'source': 'oasis', 'destination': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.duboce_park.id), 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.post('%s/redirects/' % self.API_ROOT, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        #####################################################################################
        ## Let's also test to see that a general 'ban' of a user restricts redirect creation
        #####################################################################################

        # First, ban from the region
        banned, created = BannedFromRegion.objects.get_or_create(region=self.sf)
        banned.users.add(self.edit_user)

        data = {'source': 'mission dolores park', 'destination': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.dolores_park.id), 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/redirects/%s/' % (self.API_ROOT, self.mission_dolores_park.id), data, format='json')
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Now remove the ban and it should work
        banned.users.remove(self.edit_user)

        data = {'source': 'mission dolores park', 'destination': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.dolores_park.id), 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/redirects/%s/' % (self.API_ROOT, self.mission_dolores_park.id), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Now, let's try a global ban using the banned group
        banned = Group.objects.get(name=settings.USERS_BANNED_GROUP)
        self.edit_user.groups.add(banned)

        data = {'source': 'mission dolores park', 'destination': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.duboce_park.id), 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/redirects/%s/' % (self.API_ROOT, self.mission_dolores_park.id), data, format='json')
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        ## Now remove the ban and it should work
        self.edit_user.groups.remove(banned)

        data = {'source': 'mission dolores park', 'destination': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.duboce_park.id), 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/redirects/%s/' % (self.API_ROOT, self.mission_dolores_park.id), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
