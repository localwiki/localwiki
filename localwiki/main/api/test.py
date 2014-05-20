from django.core.management import call_command
from django.conf import settings

from rest_framework import test


class APITestCase(test.APITestCase):
    API_ROOT = '/api/v4'

    def setup_auth_and_perms(self):
        call_command('reset_permissions', verbosity=0)

    def setUp(self):
        settings.IN_API_TEST = True

        super(APITestCase, self).setUp()
        self.setup_auth_and_perms()
