from urllib import quote
from urllib import unquote_plus
import mimetypes
import re
from copy import copy

from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import stringfilter
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django_randomfilenamestorage.storage import (
    RandomFilenameFileSystemStorage)

from versionutils import diff
from versionutils import versioning

import exceptions
from fields import WikiHTMLField


class Page(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, editable=False, unique=True)
    content = WikiHTMLField()

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
            raise ValidationError(_('Page name is invalid.'))

    def exists(self):
        """
        Returns:
            True if the Page currently exists in the database.
        """
        if Page.objects.filter(slug=self.slug):
            return True
        return False

    def is_front_page(self):
        return self.name.lower() == 'front page'

    def pretty_slug(self):
        if not self.name:
            return self.slug
        return name_to_url(self.name)
    pretty_slug = property(pretty_slug)

    def name_parts(self):
        return self.name.split('/')
    name_parts = property(name_parts)

    def _get_slug_related_objs(self):
        # Right now this is simply hard-coded.
        # TODO: generalize this slug pattern, perhaps with some kind of
        # AttachedSlugField or something.
        return [
            {'objs': PageFile.objects.filter(slug=self.slug),
             'unique_together': ('name', 'slug')},
        ]

    def rename_to(self, pagename):
        """
        Renames the page to `pagename`.  Moves related objects around
        accordingly.
        """
        def _get_slug_lookup(unique_together, obj, new_p):
            d = {}
            for field in unique_together:
                d[field] = getattr(obj, field)
            d['slug'] = new_p.slug
            return d

        from redirects.models import Redirect
        from redirects.exceptions import RedirectToSelf

        if Page.objects.filter(slug=slugify(pagename)):
            if slugify(pagename) == self.slug:
                # The slug is the same but we're changing the name.
                old_name = self.name
                self.name = pagename
                self.save(comment=_('Renamed from "%s"') % old_name)
                return
            else:
                raise exceptions.PageExistsError(
                    _("The page '%s' already exists!") % pagename)

        # Copy the current page into the new page, zeroing out the
        # primary key and setting a new name and slug.
        new_p = copy(self)
        new_p.pk = None
        new_p.name = pagename
        new_p.slug = slugify(pagename)
        new_p.save(comment=_('Renamed from "%s"') % self.name)

        # Get all related objects before the original page is deleted.
        related_objs = []
        for r in self._meta.get_all_related_objects():
            try:
                rel_obj = getattr(self, r.get_accessor_name())
            except:
                continue  # No object for this relation.

            # Is this a related /set/, e.g. redirect_set?
            if isinstance(rel_obj, models.Manager):
                # list() freezes the QuerySet, which we don't want to be
                # fetched /after/ we delete the page.
                related_objs.append(
                    (r.get_accessor_name(), list(rel_obj.all())))
            else:
                related_objs.append((r.get_accessor_name(), rel_obj))

        # Cache all ManyToMany values on related objects so we can restore them
        # later--otherwise they will be lost when page is deleted.
        for attname, rel_obj_list in related_objs:
            if not isinstance(rel_obj_list, list):
                rel_obj_list = [rel_obj_list]
            for rel_obj in rel_obj_list:
                rel_obj._m2m_values = dict(
                    (f.attname, list(getattr(rel_obj, f.attname).all()))
                    for f in rel_obj._meta.many_to_many)

        # Create a redirect from the starting pagename to the new pagename.
        redirect = Redirect(source=self.slug, destination=new_p)
        # Creating the redirect causes the starting page to be deleted.
        redirect.save()

        # Point each related object to the new page and save the object with a
        # 'was renamed' comment.
        for attname, rel_obj in related_objs:
            if isinstance(rel_obj, list):
                for obj in rel_obj:
                    obj.pk = None  # Reset the primary key before saving.
                    try:
                        getattr(new_p, attname).add(obj)
                        obj.save(comment=_("Parent page renamed"))
                        # Restore any m2m fields now that we have a new pk
                        for name, value in obj._m2m_values.items():
                            setattr(obj, name, value)
                    except RedirectToSelf, s:
                        # We don't want to create a redirect to ourself.
                        # This happens during a rename -> rename-back
                        # cycle.
                        continue
            else:
                # This is an easy way to set obj to point to new_p.
                setattr(new_p, attname, rel_obj)
                rel_obj.pk = None  # Reset the primary key before saving.
                rel_obj.save(comment=_("Parent page renamed"))
                # Restore any m2m fields now that we have a new pk
                for name, value in rel_obj._m2m_values.items():
                    setattr(rel_obj, name, value)

        # Do the same with related-via-slug objects.
        for info in self._get_slug_related_objs():
            unique_together = info['unique_together']
            objs = info['objs']
            for obj in objs:
                # If we already have the same object with this slug then
                # skip it. This happens when there's, say, a PageFile that's
                # got the same name that's attached to the page -- which can
                # happen during a page rename -> rename back cycle.
                obj_lookup = _get_slug_lookup(unique_together, obj, new_p)
                if obj.__class__.objects.filter(**obj_lookup):
                    continue
                obj.slug = new_p.slug
                obj.pk = None  # Reset the primary key before saving.
                obj.save(comment=_("Parent page renamed"))


class PageDiff(diff.BaseModelDiff):
    fields = ('name',
              ('content', diff.diffutils.HtmlFieldDiff),
             )


diff.register(Page, PageDiff)
versioning.register(Page)


class PageFile(models.Model):
    file = models.FileField(ugettext_lazy("file"), upload_to='pages/files/',
                            storage=RandomFilenameFileSystemStorage())
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, editable=False)

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
    def attached_to_page(self):
        try:
            p = Page.objects.get(slug=self.slug)
        except Page.DoesNotExist:
            p = Page(slug=self.slug, name=clean_name(self.slug))
        return p

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


versioning.register(PageFile)


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
    """
    Converts page name to its canonical URL path
    """
    # spaces to underscore
    # This is performance-critical, sad name_to_url can be called
    # thousands of times on some results (e.g. map points' urls).
    # Still faster than re.sub.
    value = value.strip().replace(' ', '_').replace('\t', '_'
        ).replace('\r', '_').replace('\n', '_')
    # url-encode
    value = quote(value.encode('utf-8'))
    return mark_safe(value)
name_to_url = stringfilter(name_to_url)


def url_to_name(value):
    """
    Converts URL to the intended page name
    """
    # decode URL-encoded chars
    value = unquote_plus(value.encode('utf-8')).decode('utf-8')
    return re.sub('_', ' ', value).strip()
url_to_name = stringfilter(url_to_name)


# For registration calls
import signals
import api
import feeds
