from django import forms

from .models import Page, slugify


class PageChoiceField(forms.ModelChoiceField):
    """
    Use this in ModelForms when you've got a ForeignKey to a Page.
    """
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.pop('widget', forms.widgets.TextInput)
        super(PageChoiceField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and not self.required:
            return None
        try:
            return self.queryset.filter(slug=slugify(value)).get()
        except self.queryset.model.DoesNotExist:
            raise forms.ValidationError(
                "Please enter a valid %s." % (
                    self.queryset.model._meta.verbose_name,))

    def prepare_value(self, value):
        value = super(PageChoiceField, self).prepare_value(value)
        # Turn it into a page name rather than a pk integer.
        if value:
            return Page.objects.get(pk=value).name
        return ''
