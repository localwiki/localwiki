from django.utils.translation import ugettext_lazy

from django.db import models


class Region(models.Model):
    full_name = models.CharField(max_length=255,
        help_text=ugettext_lazy("The full name of this region, e.g. 'San Francisco'"))
    short_name = models.SlugField(max_length=255, unique=True,
        help_text=ugettext_lazy("A very short name for this region, e.g. 'sf'. "
            "Spaces okay, but keep it short!"))

    def save(self, *args, **kwargs):
        self.short_name = slugify(self.short_name)
        super(Region, self).save(*args, **kwargs)


def slugify(s):
    """
    Like `page.models.slugify`, except we don't nearly as many fancy symbols.
    """
    from pages.models import slugify as page_slugify
    return page_slugify(s, keep=r"\.,'")
