from urllib import quote
from urllib import unquote_plus
import mimetypes
import re

from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import stringfilter
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from django_randomfilenamestorage.storage import (
    RandomFilenameFileSystemStorage)

from ckeditor.models import HTML5FragmentField
from versionutils import diff
from versionutils.versioning import TrackChanges

allowed_tags = ['p', 'br', 'a', 'em', 'strong', 'u', 'img', 'h1', 'h2', 'h3',
                'h4', 'h5', 'h6', 'hr', 'ul', 'ol', 'li', 'pre', 'table',
                'thead', 'tbody', 'tr', 'th', 'td', 'span', 'strike', 'sub',
                'sup', 'tt']


class Page(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, editable=False, unique=True)
    content = HTML5FragmentField(allowed_elements=allowed_tags)
    history = TrackChanges()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pages:show', args=[self.pretty_slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Page, self).save(*args, **kwargs)

    def clean(self):
        self.name = clean_name(self.name)
        if not slugify(self.name):
            raise ValidationError('Page name is invalid.')

    def pretty_slug(self):
        if not self.name:
            return self.slug
        return name_to_url(self.name)
    pretty_slug = property(pretty_slug)


class PageDiff(diff.BaseModelDiff):
    fields = ('name',
              ('content', diff.diffutils.HtmlFieldDiff),
             )


diff.register(Page, PageDiff)


class PageFile(models.Model):
    file = models.FileField(upload_to='pages/files/',
                            storage=RandomFilenameFileSystemStorage())
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, editable=False)
    history = TrackChanges()

    _rough_type_map = [(r'^audio', 'audio'),
                       (r'^video', 'video'),
                       (r'^application/pdf', 'pdf'),
                       (r'^application/msword', 'word'),
                       (r'^text/html', 'html'),
                       (r'^text', 'text'),
                       (r'^image', 'image'),
                       (r'^application/vnd.ms-powerpoint', 'powerpoint'),
                       (r'^application/vnd.ms-excel', 'excel')
                      ]

    def get_absolute_url(self):
        return reverse('pages:file',
            kwargs={'slug': self.slug, 'file': self.name})

    @property
    def rough_type(self):
        mime = self.mime_type
        if mime:
            for regex, rough_type in self._rough_type_map:
                if re.match(regex, mime):
                    return rough_type
        return 'unknown'

    @property
    def mime_type(self):
        return mimetypes.guess_type(self.name)[0]

    def is_image(self):
        return self.rough_type == 'image'

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
    """
    Normalizes page name for db lookup

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
