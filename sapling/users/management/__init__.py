from django.db.models import signals
from django.contrib.auth.models import User, Group
from django.conf import settings

from users import models as users_app


def add_all_users_to_group(sender, **kwargs):
    """
    Adds every user (except AnonymousUser) to the group specified by the
    USERS_DEFAULT_GROUP setting.
    """
    all_group, created = Group.objects.get_or_create(
                                            name=settings.USERS_DEFAULT_GROUP)
    print 'Adding users to the group "%s"' % all_group.name
    for u in User.objects.exclude(pk=settings.ANONYMOUS_USER_ID):
        u.groups.add(all_group)
        u.save()


signals.post_syncdb.connect(add_all_users_to_group, sender=users_app,
    dispatch_uid="users.management.add_all_users_to_group")
