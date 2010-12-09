from django import forms
from mikepages.models import Page
from tinymce.widgets import TinyMCE
#from ckeditor.widgets import CKEditor

class PageForm(forms.ModelForm):
    #content = forms.CharField(widget=CKEditor())
    #content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    class Meta:
        model = Page