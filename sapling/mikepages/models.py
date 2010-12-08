from django.db import models
from ckeditor.models import HTML5FragmentField

import diff

class Page(models.Model):
    name = models.CharField(max_length=100)
    content = HTML5FragmentField()
    date = models.DateTimeField(auto_now=True)
    img = models.ImageField(upload_to='mikepages_uploads', null=True, blank=True)


class PageDiff(diff.BaseModelDiff):
    fields = ( 'name', 
              ('content', diff.diffutils.HtmlFieldDiff),
              'date',
              'img'
             )
   
diff.register(Page, PageDiff)
