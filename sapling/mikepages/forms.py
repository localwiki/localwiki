from django import forms
from mikepages.models import Page
from django.template.defaultfilters import slugify


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
    
    def clean(self):
        try:
            page = Page.objects.get(slug__exact=slugify(self.cleaned_data['name']))
            if self.instance != page:
                raise forms.ValidationError('A page with this name already exists')
        except Page.DoesNotExist:
            pass
        return self.cleaned_data