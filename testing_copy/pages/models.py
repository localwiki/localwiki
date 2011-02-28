from django.db import models
from django.template.defaultfilters import slugify
from ckeditor.models import HTML5FragmentField

from versionutils import diff
from versionutils.versioning import TrackChanges


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


class PageDiff(diff.BaseModelDiff):
    fields = ('name',
              ('content', diff.diffutils.HtmlFieldDiff),
             )

diff.register(Page, PageDiff)
