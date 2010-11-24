from django.db import models
from ckeditor.models import HTML5FragmentField

import modeldiff

class Page(models.Model):
    name = models.CharField(max_length=100)
    content = HTML5FragmentField()
    date = models.DateTimeField(auto_now=True)
    img = models.ImageField(upload_to='mikepages_uploads', null=True, blank=True)


class PageDiff(modeldiff.BaseModelDiff):
    fields = ( 'name', 
              'content',
              'date',
              'img'
             )
   
modeldiff.register(Page, PageDiff)