from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import Permission, Group, User


class Command(BaseCommand):
    help = 'Resets permissions to their defaults'

    def handle(self, *args, **options):
        permissions = settings.USERS_DEFAULT_PERMISSIONS

        for g in permissions.get('auth.group', []):
            self.stdout.write('Setting permissions for group "%s"\n'
                                                            % g['name'])
            group = Group.objects.get(name=g['name'])
            group.permissions.clear()
            for p in g['permissions']:
                permission = Permission.objects.get_by_natural_key(*p)
                group.permissions.add(permission)
            group.save()

        for u in permissions.get('auth.user', []):
            self.stdout.write('Setting permissions for user "%s"\n'
                                                            % u['username'])
            user = User.objects.get(username=u['username'])
            user.user_permissions.clear()
            for p in u['user_permissions']:
                permission = Permission.objects.get_by_natural_key(*p)
                user.user_permissions.add(permission)
            user.save()

        self.stdout.write('Successfully applied default permissions\n')
