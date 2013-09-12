from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete

from models import UserProfile


def create_user_profile(sender, instance, created, raw, **kwargs):
    if raw:
        # Don't create UserProfiles when importing via loaddata - they're already
        # being imported.
        return
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)


def delete_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.delete()

# Delete UserProfile when User is deleted.  We need to do this explicitly
# because we're monkeypatching the User model (for now).
pre_delete.connect(delete_user_profile, sender=User) 
