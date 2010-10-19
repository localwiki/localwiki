from django.db import models
import modeldiff

class Page(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateTimeField(auto_now=True)
    


class PageDiff(modeldiff.BaseModelDiff):
    fields = ( 'name', 
              'content',
              'date'
             )
   
modeldiff.register(Page, PageDiff)