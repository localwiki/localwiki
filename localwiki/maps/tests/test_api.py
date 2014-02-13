import json

from rest_framework import status

from django.contrib.auth.models import User, Group
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry

from main.api.test import APITestCase
from regions.models import Region
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
        response = self.client.get('/api/maps/')
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

        data = {'page': 'http://testserver/api/pages/%s/' % self.golden_gate_park.id, 'geom': geojson, 'region': 'http://testserver/api/regions/%s/' % (self.sf.id)}
        resp = self.client.post('/api/maps/', data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_page_chained_filter(self):
        response = self.client.get('/api/maps/?page__slug__icontains=dolores')
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)

    def test_geo_filter(self):
        response = self.client.get('/api/maps/?polys__contains={ "type": "Point", "coordinates": [ -122.42724180221558, 37.75988395932576 ] }')
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)
