from urllib import quote
from urllib import unquote_plus
import re
from django.contrib.gis.db import models
from django.template.defaultfilters import stringfilter
from ckeditor.models import HTML5FragmentField

from versionutils import diff
from versionutils.versioning import TrackChanges
from django.utils.safestring import mark_safe


allowed_tags = ['p', 'a', 'em', 'strong', 'u', 'img', 'h1', 'h2', 'h3', 'h4',
                'h5', 'hr', 'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr',
                'th', 'td']


class Page(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, editable=False, unique=True)
    content = HTML5FragmentField(allowed_elements=allowed_tags)
    history = TrackChanges()

    def __unicode__(self):
        return self.name

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


diff.register(Page, PageDiff)


def slugify(value, lowercase=True, keep="\-\._'/&"):
    """Normalizes page name for db lookup or canonical URL

    Args:
        value: String or unicode object to normalize.
        lowercase: Convert to lowercase. Defaults to True.
        keep: Special non-word and non-space characters that should
            not get stripped out. Defaults to characters important to meaning.
    Returns:
        An HTML-safe, url-encoded string with special characters removed.
    """
    # decode URL-encoded chars
    value = unquote_plus(value.encode('utf-8')).decode('utf-8')

    # normalize unicode
    import unicodedata
    value = unicodedata.normalize('NFKD', unicode(value))

    # remove non-{word,space,keep} characters
    misc_characters = re.compile(('[^\w\s%s]' % keep), re.UNICODE)
    value = re.sub(misc_characters, '', value)
    value = value.strip()

    if lowercase:
        value = value.lower()

    # spaces to underscore
    value = re.sub('[_\s]+', '_', value)
    # url-encode
    value = quote(value.encode('utf-8'))
    return mark_safe(value)
slugify.is_safe = True
slugify = stringfilter(slugify)
