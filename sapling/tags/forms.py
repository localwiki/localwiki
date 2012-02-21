from django import forms

from versionutils.merging.forms import MergeMixin
from tags.models import Tag, PageTagSet, slugify
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from tags.widgets import TagEdit


def parse_tags(tagstring):
    words = [s.strip() for s in tagstring.split(',')]
    words = filter(lambda x: len(x) > 0, words)
    return list(set(words))


def tags_to_edit_string(tags):
    return ", ".join(tags)


class TagSetField(forms.ModelMultipleChoiceField):
    widget = TagEdit()

    def __init__(self, queryset, *args, **kwargs):
        super(TagSetField, self).__init__(queryset, *args, **kwargs)

    def clean(self, value):
        if not value:
            if self.required:
                raise ValidationError(self.error_messages['required'])
            else:
                return []
        self.run_validators(value)
        keys = []
        for word in parse_tags(value):
            try:
                tag, created = Tag.objects.get_or_create(slug=slugify(word),
                                                     defaults={'name': word})
                keys.append(tag.pk)
            except IntegrityError as e:
                raise ValidationError(e)
        return keys

    def prepare_value(self, value):
        if not hasattr(value, '__iter__'):
            return value
        tags = [t.name for t in self.queryset.filter(**{'pk__in': value})]
        return tags_to_edit_string(tags)


class PageTagSetForm(MergeMixin, forms.ModelForm):
    class Meta:
        model = PageTagSet
        fields = ('tags',)

    tags = TagSetField(queryset=Tag.objects.all(), required=False)

    def merge(self, yours, theirs, ancestor):
        # NOTE: I think something's not right here with versioning
        your_set = set(yours['tags'])
        their_set = set(theirs['tags'])
        if ancestor:
            old_set = set(ancestor['tags'])
        else:
            old_set = set()
        common = your_set.intersection(their_set)
        merged = your_set.union(their_set).difference(old_set).union(common)
        yours['tags'] = list(merged)
        return yours
