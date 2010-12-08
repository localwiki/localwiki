from django.db import models
import diff

class Page(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateTimeField(auto_now=True)
    img = models.ImageField(upload_to='mikepages_uploads')


class PageDiff(diff.BaseModelDiff):
    fields = ( 'name', 
              ('content', diff.diffutils.HtmlFieldDiff),
              'date',
              'img'
             )
   
diff.register(Page, PageDiff)
