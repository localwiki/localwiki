import json

from rest_framework import status
from guardian.shortcuts import assign_perm, remove_perm

from django.contrib.auth.models import User, Group
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry

from main.api.test import APITestCase
from regions.models import Region, BannedFromRegion
from pages.models import Page

from .. models import MapData


class MapAPITests(APITestCase):
    def setUp(self):
        super(MapAPITests, self).setUp()

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

        self.golden_gate_park = Page(name="Golden Gate Park", content="<p>Hi</p>", region=self.sf)
        self.golden_gate_park.save()

        self.dolores_park = Page(name="Dolores Park", content="<p>Hi</p>", region=self.sf)
        self.dolores_park.save()

        self.duboce_park = Page(name="Duboce Park", content="<p>Hi</p>", region=self.sf)
        self.duboce_park.save()

        self.dolores_park_map = MapData(page=self.dolores_park, region=self.sf)
        self.dolores_park_map.geom = GEOSGeometry("""
        { "type": "GeometryCollection", "geometries": [
          {
          "type": "Polygon",
          "coordinates": [
            [
              [
                -122.42835760116576,
                37.76128348360843
              ],
              [
                -122.42799282073973,
                37.75812815505155
              ],
              [
                -122.42591142654419,
                37.758297799795336
              ],
              [
                -122.42627620697021,
                37.761402229904654
              ],
              [
                -122.42835760116576,
                37.76128348360843
              ]
            ]
          ]
        }]
      }""")
        self.dolores_park_map.save()

        self.duboce_park_map = MapData(page=self.duboce_park, region=self.sf)
        self.duboce_park_map.geom = GEOSGeometry("""
        { "type": "GeometryCollection", "geometries": [

           {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -122.43505239486696,
                  37.770443352285376
                ],
                [
                  -122.43490219116211,
                  37.76917121614543
                ],
                [
                  -122.431640625,
                  37.769408683219545
                ],
                [
                  -122.43179082870485,
                  37.76991753866766
                ],
                [
                  -122.43460178375243,
                  37.769713996908635
                ],
                [
                  -122.43505239486696,
                  37.770443352285376
                ]
              ]
            ]
          } 

        ]
      }
      """)
        self.duboce_park_map.save()

    def test_map_list(self):
        response = self.client.get('%s/maps/' % self.API_ROOT)
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 2)

    def test_map_simple_post(self):
        self.client.force_authenticate(user=self.edit_user)

        geojson = """
        { "type": "GeometryCollection", "geometries": [
            {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -122.42835760116576,
                  37.76128348360843
                ],
                [
                  -122.42799282073973,
                  37.75812815505155
                ],
                [
                  -122.42591142654419,
                  37.758297799795336
                ],
                [
                  -122.42627620697021,
                  37.761402229904654
                ],
                [
                  -122.42835760116576,
                  37.76128348360843
                ]
              ]
            ]
          }]
        }"""

        data = {'page': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.golden_gate_park.id), 'geom': geojson, 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.post('%s/maps/' % self.API_ROOT, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_page_chained_filter(self):
        response = self.client.get('%s/maps/?page__slug__icontains=dolores' % self.API_ROOT)
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)

    def test_geo_filter(self):
        response = self.client.get('%s/maps/?polys__contains={ "type": "Point", "coordinates": [ -122.42724180221558, 37.75988395932576 ] }' % self.API_ROOT)
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)

    def test_map_permissions(self):
        self.client.force_authenticate(user=self.edit_user)

        # Make it so only edit_user_2 can edit the Dolores Park page
        assign_perm('change_page', self.edit_user_2, self.dolores_park)

        # Now try and update the "dolores park" map as edit_user
        geojson = """
        { "type": "GeometryCollection", "geometries": [
            {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -122.42835760116576,
                  37.76128348360843
                ],
                [
                  -122.42799282073973,
                  37.75812815505155
                ],
                [
                  -122.42591142654419,
                  37.758297799795336
                ],
                [
                  -122.42627620697021,
                  37.761402229904654
                ],
                [
                  -122.42835760116576,
                  37.76128348360843
                ]
              ]
            ]
          }]
        }"""

        data = {'page': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.dolores_park.id), 'geom': geojson, 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/maps/%s/' % (self.API_ROOT, self.dolores_park_map.id), data, format='json')
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Now remove the permission and it should work
        remove_perm('change_page', self.edit_user_2, self.dolores_park)

        data = {'page': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.dolores_park.id), 'geom': geojson, 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/maps/%s/' % (self.API_ROOT, self.dolores_park_map.id), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        ##################################################################################
        # Let's also test a normal POST to a protected page which doesn't yet have a map
        ##################################################################################
        new_park = Page(name="New Park", content="<p>Hi</p>", region=self.sf)
        new_park.save()

        # Make it so only edit_user_2 can edit the Dolores Park page
        assign_perm('change_page', self.edit_user_2, new_park)

        # Now try and create the "New Park" map as edit_user
        geojson = """
        { "type": "GeometryCollection", "geometries": [
            {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -122.42835760116576,
                  37.76128348360843
                ],
                [
                  -122.42799282073973,
                  37.75812815505155
                ],
                [
                  -122.42591142654419,
                  37.758297799795336
                ],
                [
                  -122.42627620697021,
                  37.761402229904654
                ],
                [
                  -122.42835760116576,
                  37.76128348360843
                ]
              ]
            ]
          }]
        }"""

        data = {'page': 'http://testserver%s/pages/%s/' % (self.API_ROOT, new_park.id), 'geom': geojson, 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.post('%s/maps/' % self.API_ROOT, data, format='json')
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Now remove the permission and it should work
        remove_perm('change_page', self.edit_user_2, new_park)

        data = {'page': 'http://testserver%s/pages/%s/' % (self.API_ROOT, new_park.id), 'geom': geojson, 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.post('%s/maps/' % self.API_ROOT, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        ##################################################################################
        # Let's also test to see that a general 'ban' of a user restricts map editing
        ##################################################################################

        # First, ban from the region
        banned, created = BannedFromRegion.objects.get_or_create(region=self.sf)
        banned.users.add(self.edit_user)

        # Now try and update the "dolores park" map as edit_user
        geojson = """
        { "type": "GeometryCollection", "geometries": [
            {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -122.42835760116576,
                  37.76128348360843
                ],
                [
                  -122.42799282073973,
                  37.75812815505155
                ],
                [
                  -122.42591142654419,
                  37.758297799795336
                ],
                [
                  -122.42627620697021,
                  37.761402229904654
                ],
                [
                  -122.42835760116576,
                  37.76128348360843
                ]
              ]
            ]
          }]
        }"""

        data = {'page': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.dolores_park.id), 'geom': geojson, 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/maps/%s/' % (self.API_ROOT, self.dolores_park_map.id), data, format='json')
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Now remove the ban and it should work
        banned.users.remove(self.edit_user)

        data = {'page': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.dolores_park.id), 'geom': geojson, 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/maps/%s/' % (self.API_ROOT, self.dolores_park_map.id), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Now, let's try a global ban using the banned group
        banned = Group.objects.get(name=settings.USERS_BANNED_GROUP)
        self.edit_user.groups.add(banned)

        # Now try and update the "dolores park" map as edit_user
        geojson = """
        { "type": "GeometryCollection", "geometries": [
            {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -122.42835760116576,
                  37.76128348360843
                ],
                [
                  -122.42799282073973,
                  37.75812815505155
                ],
                [
                  -122.42591142654419,
                  37.758297799795336
                ],
                [
                  -122.42627620697021,
                  37.761402229904654
                ],
                [
                  -122.42835760116576,
                  37.76128348360843
                ]
              ]
            ]
          }]
        }"""

        data = {'page': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.dolores_park.id), 'geom': geojson, 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/maps/%s/' % (self.API_ROOT, self.dolores_park_map.id), data, format='json')
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Now remove the ban and it should work
        self.edit_user.groups.remove(banned)

        data = {'page': 'http://testserver%s/pages/%s/' % (self.API_ROOT, self.dolores_park.id), 'geom': geojson, 'region': 'http://testserver%s/regions/%s/' % (self.API_ROOT, self.sf.id)}
        resp = self.client.put('%s/maps/%s/' % (self.API_ROOT, self.dolores_park_map.id), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
