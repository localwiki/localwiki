from django.core.management import call_command

from rest_framework import test


class APITestCase(test.APITestCase):
    def setup_auth_and_perms(self):
        call_command('reset_permissions', verbosity=0)

    def setUp(self):
        super(APITestCase, self).setUp()
        self.setup_auth_and_perms()
