from urllib import quote
from urllib import unquote_plus
import re
import string
from django.db import models
from django.template.defaultfilters import slugify, stringfilter
from ckeditor.models import HTML5FragmentField

from versionutils import diff
from versionutils.versioning import TrackChanges
from django.utils.safestring import mark_safe


class Page(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, editable=False, unique=True)
    content = HTML5FragmentField(
        allowed_elements=['p', 'a', 'em', 'strong', 'img']
    )
    history = TrackChanges()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Page, self).save(*args, **kwargs)

    def pretty_slug(self):
        return slugify(self.name, lowercase=False)
    pretty_slug = property(pretty_slug)


class PageDiff(diff.BaseModelDiff):
    fields = ('name',
              ('content', diff.diffutils.HtmlFieldDiff),
             )


def slugify(value, lowercase=True):
    """Normalizes page name.
    """
    stuff_we_like = '-_/&:\'"'  # special characters we like in a url
    import unicodedata
    # normalize unicode
    value = unicodedata.normalize('NFKD', value)
    # decode URL-encoded chars
    value = unquote_plus(value)
    # remove non-{word,space,stuff we like} characters
    misc_characters = re.compile(('[^\w\s%r]' % stuff_we_like), re.UNICODE)
    value = re.sub(misc_characters, '', value).strip()
    if lowercase:
        value = value.lower()
    # encode as utf-8
    value = value.encode('utf-8', 'ignore')
    # replace spaces and repeating underscores with underscores
    value = re.sub('[_\s]+', '_', value)
    # do we want this? disabled. url-encode, preserving stuff we like:
    # value = quote(value, stuff_we_like)
    return mark_safe(value)
slugify.is_safe = True
slugify = stringfilter(slugify)


diff.register(Page, PageDiff)
