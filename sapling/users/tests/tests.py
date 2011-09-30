from django.test import TestCase
from django.conf import settings

from utils import TestSettingsManager
from models import *
from django.contrib.auth.models import User, Permission, Group
from guardian.shortcuts import assign

mgr = TestSettingsManager()
INSTALLED_APPS = list(settings.INSTALLED_APPS)
INSTALLED_APPS.append('users.tests')
mgr.set(INSTALLED_APPS=INSTALLED_APPS)
mgr.set(USERS_BANNED_GROUP='Banned')


class RestrictiveBackendTest(TestCase):
    def setUp(self):
        self.user = User(username='TestUser', email='blah@blah.com',
                          password='test123')
        self.user.save()
        self.group = Group.objects.create(name='Cool group')
        self.user.groups.add(self.group)
        self.user.save()

    def tearDown(self):
        self.user.delete()
        self.group.delete()

    def test_inactive_user_blocked(self):
        t = Thing(name='Test thing')
        t.save()
        self.user.is_active = False
        self.user.save()
        assign('change_thing', self.user, t)
        self.assertFalse(self.user.has_perm('tests.change_thing', t))

    def test_banned_user_blocked(self):
        banned = Group.objects.get(name=settings.USERS_BANNED_GROUP)
        t = Thing(name='Test thing')
        t.save()
        assign('change_thing', self.user, t)
        self.assertTrue(self.user.has_perm('tests.change_thing', t))
        self.user.groups.add(banned)
        self.user.save()
        self.assertFalse(self.user.has_perm('tests.change_thing', t))

    def test_admin_not_blocked(self):
        t = Thing(name='Test thing')
        t.save()
        self.user.is_superuser = True
        self.assertTrue(self.user.has_perm('tests.change_thing', t))
        assign('change_thing', self.user, t)
        self.assertTrue(self.user.has_perm('tests.change_thing', t))

        # let's ban the admin, should still have access
        banned = Group.objects.get(name=settings.USERS_BANNED_GROUP)
        self.user.groups.add(banned)
        self.user.save()
        self.assertTrue(self.user.has_perm('tests.change_thing', t))

        # inactive is a global Django concept, so should obey it
        self.user.is_active = False
        self.user.save()
        self.assertFalse(self.user.has_perm('tests.change_thing', t))

    def test_object_permissions_win_over_user(self):
        t = Thing(name='Test thing')
        t.save()

        perm = Permission.objects.get(codename="add_thing")
        self.user.user_permissions.add(perm)
        perm = Permission.objects.get(codename="change_thing")
        self.user.user_permissions.add(perm)
        perm = Permission.objects.get(codename="delete_thing")
        self.user.user_permissions.add(perm)
        self.user.save()

        self.assertTrue(self.user.has_perm('tests.change_thing', t))
        self.assertTrue(self.user.has_perm('tests.add_thing', t))
        self.assertTrue(self.user.has_perm('tests.delete_thing', t))

        assign('change_thing', self.user, t)  # per-object permission

        self.assertTrue(self.user.has_perm('tests.change_thing', t))
        self.assertFalse(self.user.has_perm('tests.add_thing', t))
        self.assertFalse(self.user.has_perm('tests.delete_thing', t))

    def test_object_permissions_win_over_group(self):
        t = Thing(name='Test thing')
        t.save()

        perm = Permission.objects.get(codename="add_thing")
        self.group.permissions.add(perm)
        perm = Permission.objects.get(codename="change_thing")
        self.group.permissions.add(perm)
        perm = Permission.objects.get(codename="delete_thing")
        self.group.permissions.add(perm)
        self.user.save()

        self.assertTrue(self.user.has_perm('tests.change_thing'))
        self.assertTrue(self.user.has_perm('tests.add_thing'))
        self.assertTrue(self.user.has_perm('tests.delete_thing'))

        self.assertTrue(self.user.has_perm('tests.change_thing', t))
        self.assertTrue(self.user.has_perm('tests.add_thing', t))
        self.assertTrue(self.user.has_perm('tests.delete_thing', t))

        assign('change_thing', self.group, t)  # per-object permission

        self.assertTrue(self.user.has_perm('tests.change_thing', t))
        self.assertFalse(self.user.has_perm('tests.add_thing', t))
        self.assertFalse(self.user.has_perm('tests.delete_thing', t))
