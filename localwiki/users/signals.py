from django.contrib.auth.models import User
from django.db.models.signals import post_save

from models import UserProfile


def create_user_profile(sender, instance, created, raw, **kwargs):
    if raw:
        # Don't create UserProfiles when importing via loaddata - they're already
        # being imported.
        return
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)
