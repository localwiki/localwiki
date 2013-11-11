from django import forms
from django.utils.translation import  ugettext_lazy as _

from ckeditor.models import HTML5FragmentField


class WikiHTMLField(HTML5FragmentField):
    allowed_elements = [
        'p', 'br', 'a', 'em', 'strong', 'u', 'img', 'h1', 'h2', 'h3',
        'h4', 'h5', 'h6', 'hr', 'ul', 'ol', 'li', 'pre', 'table',
        'thead', 'tbody', 'tr', 'th', 'td', 'span', 'strike', 'sub',
        'sup', 'tt', 'input']
    
    allowed_attributes_map = {
        'p': ['class', 'style'],
        'h1': ['style'],
        'h2': ['style'],
        'h3': ['style'],
        'h4': ['style'],
        'h5': ['style'],
        'h6': ['style'],
        'ul': ['class'],
        'a': ['class', 'name', 'href', 'style'],
        'img': ['class', 'src', 'alt', 'title', 'style'],
        'span': ['class', 'style'],
        'table': ['class', 'style'],
        'th': ['class', 'colspan', 'rowspan', 'style'],
        'td': ['class', 'colspan', 'rowspan', 'style'],
        'input': ['class', 'type', 'value']
    }
    
    allowed_styles_map = {
        'p': ['text-align'],
        'h1': ['text-align'],
        'h2': ['text-align'],
        'h3': ['text-align'],
        'h4': ['text-align'],
        'h5': ['text-align'],
        'h6': ['text-align'],
        'img': ['width', 'height'],
        'span': ['width', 'height'],
        'table': ['width', 'height'],
        'th': ['text-align', 'background-color'],
        'td': ['text-align', 'background-color', 'width',
               'height', 'vertical-align'],
        'a': ['width']
    }
    
    rename_elements = {'b': 'strong', 'i': 'em'}

    def __init__(self, *args, **kwargs):
        super(WikiHTMLField, self).__init__(*args, **kwargs)
        self.allowed_elements = self.__class__.allowed_elements
        self.allowed_attributes_map = self.__class__.allowed_attributes_map
        self.allowed_styles_map = self.__class__.allowed_styles_map
        self.rename_elements = self.__class__.rename_elements


class PageChoiceField(forms.ModelChoiceField):
    """
    Use this in ModelForms when you've got a ForeignKey to a Page.
    """
    def __init__(self, *args, **kwargs):
        from .models import Page
        kwargs['widget'] = kwargs.pop('widget', forms.widgets.TextInput)

        # Limit to the specified region
        region = kwargs.pop('region', None)
        kwargs['queryset'] = Page.objects.filter(region=region)
        super(PageChoiceField, self).__init__(*args, **kwargs)

    def clean(self, value):
        from .models import slugify

        if not value and not self.required:
            return None
        try:
            return self.queryset.filter(slug=slugify(value)).get()
        except self.queryset.model.DoesNotExist:
            raise forms.ValidationError(
                _("Page %s does not exist!  Please enter a valid page name.") % (
                    self.queryset.model._meta.verbose_name,))

    def prepare_value(self, value):
        from .models import Page

        if isinstance(value, basestring):
            # already a page name
            return
        value = super(PageChoiceField, self).prepare_value(value)
        # Turn it into a page name rather than a pk integer.
        if value:
            return Page.objects.get(pk=value).name
        return ''


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^pages\.fields"])
except ImportError:
    pass
