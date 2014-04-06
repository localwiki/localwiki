from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User

from follow.models import Follow

from versionutils.versioning.constants import TYPE_DELETED_CASCADE
from pages.models import Page


# Notification types
OWN_USER_PAGE = 0
PAGE_DELETED = 1


def notify_page_edited(user, page, notification_type=None):
    if notification_type == OWN_USER_PAGE:
        print "<< notify %s that own page %s was edited >>" % (user, page)
    else:
        print "<< notify %s that %s was edited >>" % (user, page)


def notify_page_deleted(user, page, notification_type=None):
    if notification_type == OWN_USER_PAGE:
        print "<< notify %s that own page %s was deleted >>" % (user, page)
    else:
        print "<< notify %s that %s was deleted >>" % (user, page)


def follow_own_user_object(sender, instance, created, raw, **kwargs):
    if raw:
        # Don't create when importing via loaddata - they're already
        # being imported.
        return
    if created:
        f = Follow(user=instance, target_user=instance)
        f.save()


def is_user_page(page):
    return page.slug.startswith('users/')


def notify_user_page_owner(page, edit_type=None):
    username = page.slug[6:]
    u = User.objects.filter(username__iexact=username)
    if not u:
        return
    user = u[0]

    # The user can opt to stop following theirself.
    if not Follow.objects.is_following(user, user):
        return

    if edit_type == PAGE_DELETED:
        notify_page_deleted(user, page, notification_type=OWN_USER_PAGE)
    else:
        notify_page_edited(user, page, notification_type=OWN_USER_PAGE)


def follows_before_cascade(past_follows):
    follows = set()
    # The first set of revisions should all be deleted by cascade, so let's get just those. 
    for v in past_follows:
        if v.version_info.type != TYPE_DELETED_CASCADE:
            break
        follows.add(v) 
    return follows


def re_add_users_following_before_delete(instance):
    # First, let's see if this page existed before.
    if instance.versions.all().count() > 2:
        # Now let's get the version before it was deleted
        before_delete = instance.versions.all()[2]

        past_follows = Follow.versions.filter(
            target_page__id=before_delete.id
        )

        # Now, re-follow.
        for follow in follows_before_cascade(past_follows):
            f = Follow(user=follow.user, target_page=instance)
            # For versioning purposes, let's keep the same pk
            # we had before delete.
            f.id = follow.id
            f.save()


def notify_followers_page_edited(sender, instance, created, raw, **kwargs):
    if raw:
        # We don't want to do this via loaddata.
        return
    followers = Follow.objects.get_follows(instance)
    if created:
        # Because the page may have been deleted, we want to make sure to
        # re-add it to the follow list of users who were following right
        # before the page was deleted.
        re_add_users_following_before_delete(instance)
        
    for fobj in followers:
        # Skip the notification if the editor is the follower
        if fobj.user == instance.versions.most_recent().version_info.user:
            continue
        notify_page_edited(fobj.user, instance)

    if is_user_page(instance):
        notify_user_page_owner(instance)


def notify_followers_page_deleted(sender, instance, **kwargs):
    # Instance is gone, and so are the Follow objects (deleted via cascade)
    # so we have to use a historical lookup here.  We can't use the
    # pre_delete signal here because then we don't have access to who the
    # most recent page editor, edit type, etc are.
    most_recent_page_id = instance.versions.most_recent().id 
    old_follows = Follow.versions.filter(target_page__id=most_recent_page_id)

    for follow in follows_before_cascade(old_follows):
        # Skip the notification if the editor is the follower
        if follow.user == instance.versions.most_recent().version_info.user:
            continue
        notify_page_deleted(follow.user, instance)

    if is_user_page(instance):
        notify_user_page_owner(instance, edit_type=PAGE_DELETED)


post_save.connect(follow_own_user_object, sender=User)
post_save.connect(notify_followers_page_edited, sender=Page)
post_delete.connect(notify_followers_page_deleted, sender=Page)
