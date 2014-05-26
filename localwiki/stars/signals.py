from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.mail.utils import DNS_NAME
from django.conf import settings

from actstream import action
from follow.models import Follow
from follow.signals import followed as followed_signal
from templated_email import send_templated_mail

from utils import get_base_uri
from versionutils.versioning.constants import TYPE_REVERTED, TYPE_DELETED_CASCADE, TYPE_REVERTED_DELETED_CASCADE
from pages.models import Page
from regions.models import Region


# Notification types
OWN_USER_PAGE = 0
PAGE_DELETED = 1


def get_headers(page):
    """
    Return a dictionary of the special email headers for this
    `page`.  Supports email threading.
    """
    # Let's keep the reply-to ID the same even if the capitalization of the page
    # is changed.
    p = Page(
        name=page.name.lower(),
        region=page.region,
        content=""
    )
    reply_to_id = "</page%s@%s>" % (p.get_absolute_url(), DNS_NAME)

    return {
        'In-Reply-To': reply_to_id,
        'References': reply_to_id,
    }


def notify_page_edited(user, page, notification_type=None):
    if notification_type == OWN_USER_PAGE:
        template_name = 'stars/own_userpage_edited'
    else:
        template_name = 'stars/page_edited'

    page_hist = page.versions.most_recent()

    diff_url = reverse('pages:compare-dates', kwargs={
        'slug': page.pretty_slug,
        'region': page.region.slug,
        'date1': page_hist.version_info.date,
    })
    # In plaintext email, we want the period escaped
    # because some clients don't include it in the URL.
    diff_url_plaintext = diff_url.replace('.', '%2E')

    if page_hist.version_info.user:
        username = page_hist.version_info.user.username
        user_url = page_hist.version_info.user.get_absolute_url()
        user_with_link = '<a href="%s">%s</a>' % (user_url, username)
    else:
        username = page_hist.version_info.user_ip
        user_with_link = username

    comment_text = page_hist.version_info.comment
    if comment_text:
        comment_text = ' ' + _('Their edit comment was "%s".' % comment_text)

    send_templated_mail(
        template_name=template_name,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        headers=get_headers(page),
        context={
            'page': page,
            'pagename': page.name,
            'page_url': page.get_absolute_url(),
            'comment_text': comment_text,
            'user_with_link': user_with_link,
            'region_name': page.region.full_name,
            'region_url': page.region.get_absolute_url(),
            'diff_url': diff_url,
            'username': username,
            'diff_url_plaintext': diff_url_plaintext,
            'page_hist': page_hist,
            'base_uri': get_base_uri(),
        },
    )


def notify_page_deleted(user, page, notification_type=None):
    if notification_type == OWN_USER_PAGE:
        template_name = 'stars/own_userpage_deleted'
    else:
        template_name = 'stars/page_deleted'

    page_hist = page.versions.most_recent()

    if page_hist.version_info.user:
        username = page_hist.version_info.user.username
        user_url = page_hist.version_info.user.get_absolute_url()
        user_with_link = '<a href="%s">%s</a>' % (user_url, username)
    else:
        username = page_hist.version_info.user_ip
        user_with_link = username

    comment_text = page_hist.version_info.comment
    if comment_text:
        comment_text = ' ' + _('Their edit comment was "%s".' % comment_text)

    history_url = reverse('pages:history', kwargs={
        'slug': page.pretty_slug,
        'region': page.region.slug,
    })

    send_templated_mail(
        template_name=template_name,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        headers=get_headers(page),
        context={
            'page': page,
            'pagename': page.name,
            'page_url': page.get_absolute_url(),
            'comment_text': comment_text,
            'user_with_link': user_with_link,
            'region_name': page.region.full_name,
            'region_url': page.region.get_absolute_url(),
            'history_url': history_url,
            'username': username,
            'page_hist': page_hist,
            'base_uri': get_base_uri(),
        },
    )



def follow_own_user_object(sender, instance, created, raw, **kwargs):
    if raw or instance.id == settings.ANONYMOUS_USER_ID:
        # Don't create when importing via loaddata - they're already
        # being imported.
        return
    if settings.IN_API_TEST:
        # XXX TODO Due to some horrible, difficult to figure out bug in
        # how force_authenticate() works in the API tests,
        # we have to skip signals here :/
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
            # We set TYPE_REVERTED here because it's slightly
            # more accurate than the (default) TYPE_ADDED.
            f._history_type = TYPE_REVERTED
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

    if not instance.versions.all().count():
        # Page was deleted by a global admin, so let's not notify
        return

    most_recent_page_id = instance.versions.most_recent().id 
    old_follows = Follow.versions.filter(target_page__id=most_recent_page_id)

    for follow in follows_before_cascade(old_follows):
        # Skip the notification if the editor is the follower
        if follow.user == instance.versions.most_recent().version_info.user:
            continue
        notify_page_deleted(follow.user, instance)

    if is_user_page(instance):
        notify_user_page_owner(instance, edit_type=PAGE_DELETED)


def notify_follow_action(user, target, instance, **kwargs):
    """
    Notify this user's followers of certain follow actions taken by
    this user.
    """
    if (instance.versions.all().exists() and
        instance.versions.most_recent().version_info.type in
            (TYPE_DELETED_CASCADE, TYPE_REVERTED_DELETED_CASCADE)):
        # Don't notify when this is a re-created follow via a
        # revert.
        # XXX TODO: Revert the original Follow object so this follow
        # action appears in the activity feed. For now, it won't show
        # after the page has been deleted.
        return

    if isinstance(target, User):
        if user == target:
            # Don't alert that the user followed themselves.
            return
        action.send(user, verb='followed user', action_object=target)
    elif isinstance(target, Page):
        action.send(user, verb='followed page', action_object=target)
    elif isinstance(target, Region):
        action.send(user, verb='followed region', action_object=target)

if not settings.DISABLE_FOLLOW_SIGNALS:
    post_save.connect(follow_own_user_object, sender=User)
    post_save.connect(notify_followers_page_edited, sender=Page)
    post_delete.connect(notify_followers_page_deleted, sender=Page)
    followed_signal.connect(notify_follow_action, dispatch_uid='follow.user')
