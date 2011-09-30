from django.db.models import signals
from django.contrib.auth.models import User, Group
from django.conf import settings
from guardian.management import create_anonymous_user

from users import models as users_app


def create_banned_group(sender, **kwargs):
    """
    If USERS_BANNED_GROUP setting is defined, creates the group.
    """
    banned_group = getattr(settings, 'USERS_BANNED_GROUP', None)
    if banned_group and not Group.objects.filter(name=banned_group).exists():
        print 'Creating the banned group "%s"' % banned_group
        Group.objects.create(name=banned_group)


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


def add_anonymous_user_to_anonymous_group(sender, **kwargs):
    """
    Adds AnonymousUser to group specified by the USERS_ANONYMOUS_GROUP setting.
    """
    anon_group, created = Group.objects.get_or_create(
                                        name=settings.USERS_ANONYMOUS_GROUP)
    create_anonymous_user(sender, **kwargs)  # we need AnonymousUser to exist
    print 'Adding AnonymousUser to the group "%s"' % anon_group.name
    u = User.objects.get(pk=settings.ANONYMOUS_USER_ID)
    u.groups.add(anon_group)
    u.save()


signals.post_syncdb.connect(add_anonymous_user_to_anonymous_group,
    sender=users_app,
    dispatch_uid="users.management.add_anonymous_user_to_anonymous_group")

signals.post_syncdb.connect(add_all_users_to_group, sender=users_app,
    dispatch_uid="users.management.add_all_users_to_group")

signals.post_syncdb.connect(create_banned_group, sender=users_app,
    dispatch_uid="users.management.create_banned_group")
