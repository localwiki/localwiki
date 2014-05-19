from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.conf import settings

from south.models import MigrationHistory

from models import UserProfile


def create_user_profile(sender, instance, created, raw, **kwargs):
    if raw or instance.id == settings.ANONYMOUS_USER_ID:
        # Don't create UserProfiles when importing via loaddata - they're already
        # being imported.
        return
    if created:
        # Check to make sure the UserProfile migration was run first.
        # We have to check this because django-guardian creates AnonymousUser
        # on a post_syncdb signal.  TODO: this will be fixable in Django 1.7 or 1.8
        # with the post_migrate signal (guardian should use post_migrate and not
        # post_syncdb).
        if MigrationHistory.objects.filter(app_name='users').exists():
            UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)


def delete_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.delete()

# Delete UserProfile when User is deleted.  We need to do this explicitly
# because we're monkeypatching the User model (for now).
pre_delete.connect(delete_user_profile, sender=User) 
