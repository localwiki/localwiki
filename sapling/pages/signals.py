from django.db.models.signals import pre_save

from redirects.models import Redirect

from models import Page


def _delete_page(sender, instance, raw, **kws):
    # Delete the source page if it exists.
    if Page.objects.filter(slug=instance.source):
        p = Page.objects.get(slug=instance.source)
        p.delete(comment="Redirect created")

# When a Redirect is created we want to delete the source Page if it
# exists.  This is so the redirect (which works via 404 fall-through)
# will be immediately functional.
pre_save.connect(_delete_page, sender=Redirect)
