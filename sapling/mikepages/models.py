from django.db import models
import modeldiff

class Page(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateTimeField(auto_now=True)
    img = models.ImageField(upload_to='mikepages_uploads')


class PageDiff(modeldiff.BaseModelDiff):
    fields = ( 'name', 
              ('content', modeldiff.diffutils.HtmlFieldDiff),
              'date',
              'img'
             )
   
modeldiff.register(Page, PageDiff)
