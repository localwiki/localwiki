from urllib import quote
from urllib import unquote_plus
import re

from django.contrib.gis.db import models
from django.template.defaultfilters import stringfilter
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from ckeditor.models import HTML5FragmentField
from versionutils import diff
from versionutils.versioning import TrackChanges

allowed_tags = ['p', 'a', 'em', 'strong', 'u', 'img', 'h1', 'h2', 'h3', 'h4',
                'h5', 'hr', 'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr',
                'th', 'td', 'span']


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

    def clean(self):
        self.name = clean_name(self.name)
        if not slugify(self.name):
            raise ValidationError('Page name is invalid.')

    def pretty_slug(self):
        return name_to_url(self.name)
    pretty_slug = property(pretty_slug)


class PageDiff(diff.BaseModelDiff):
    fields = ('name',
              ('content', diff.diffutils.HtmlFieldDiff),
             )


diff.register(Page, PageDiff)


class PageImage(models.Model):
    file = models.ImageField(upload_to='pages/images/')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, editable=False)

    class Meta:
        unique_together = ('slug', 'name')
        ordering = ['-id']


def clean_name(name):
    # underscores are used to namespace special URLs, so let's remove them
    name = re.sub('_', ' ', name).strip()
    # we allow / in page names so we want to strip each bit between slashes
    name = '/'.join([part.strip()
                     for part in name.split('/') if slugify(part)])
    return name


def slugify(value, keep=r"\-\.,'\"/!@$%&*()"):
    """Normalizes page name for db lookup

    Args:
        value: String or unicode object to normalize.
        keep: Special non-word and non-space characters that should not get
        stripped out and contribute to a slug's uniqueness. Defaults to
        characters important to meaning.
    Returns:
        Lowercase string with special characters removed.
    """
    value = url_to_name(value)

    # normalize unicode
    import unicodedata
    value = unicodedata.normalize('NFKD', unicode(value))

    # remove non-{word,space,keep} characters
    misc_characters = re.compile(('[^\w\s%s]' % keep), re.UNICODE)
    value = re.sub(misc_characters, '', value)
    value = value.strip()
    value = re.sub('[_\s]+', ' ', value)

    return value.lower()
slugify = stringfilter(slugify)


def name_to_url(value):
    """Converts page name to its canonical URL path
    """
    # spaces to underscore
    value = re.sub('[\s]', '_', value.strip())
    # url-encode
    value = quote(value.encode('utf-8'))
    return mark_safe(value)
name_to_url.is_safe = True
name_to_url = stringfilter(name_to_url)


def url_to_name(value):
    """Converts URL to the intended page name
    """
    # decode URL-encoded chars
    value = unquote_plus(value.encode('utf-8')).decode('utf-8')
    return re.sub('_', ' ', value).strip()
url_to_name = stringfilter(url_to_name)
