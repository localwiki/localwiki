import json

from django.contrib.auth.models import User

from main.api.test import APITestCase
from rest_framework import status


class UserAPITests(APITestCase):
    def setUp(self):
        self.philip = User(username='philipn', email='blah@blah.com',
                          password='test123')
        self.philip.save()
        self.marina = User(username='mk30', email='blah2@blah.com',
                          password='test123')
        self.marina.save()

    def test_user_list(self):
        response = self.client.get('%s/users/' % self.API_ROOT)
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 3)

    def test_user_detail(self):
        response = self.client.get('%s/users/?username=philipn' % self.API_ROOT)
        jresp = json.loads(response.content)
        self.assertEqual(len(jresp['results']), 1)
        self.assertEqual(jresp['results'][0]['username'], 'philipn')
