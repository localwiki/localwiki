from django import forms

from versionutils.merging.forms import MergeMixin
from tags.models import Tag, PageTagSet, slugify, TagsFieldDiff
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.translation import ugettext as _, ungettext
from tags.widgets import TagEdit
from versionutils.versioning.forms import CommentMixin


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
        return Tag.objects.filter(pk__in=keys)

    def prepare_value(self, value):
        if not hasattr(value, '__iter__'):
            return value
        tags = [t.name for t in self.queryset.filter(**{'pk__in': value})]
        return tags_to_edit_string(tags)


class PageTagSetForm(MergeMixin, CommentMixin, forms.ModelForm):
    class Meta:
        model = PageTagSet
        fields = ('tags',)
        exclude = ('comment',)  # we generate comment automatically

    tags = TagSetField(queryset=Tag.objects.all(), required=False)

    def pluralize_tag(self, list):
        if len(list) > 1:
            return Tag._meta.verbose_name_plural.lower()
        return Tag._meta.verbose_name.lower()

    def get_save_comment(self):
        comments = []
        short_comments = []
        previous = self.instance.pk and self.instance.tags or None
        d = TagsFieldDiff(previous, self.cleaned_data['tags'])
        diff = d.get_diff()
        deleted = ['"%s"' % t.name for t in diff['deleted']]
        added = ['"%s"' % t.name for t in diff['added']]
        if deleted:
            tag_name_pluralized = self.pluralize_tag(deleted)
            comments.append(ungettext(
                        'removed %(name)s %(deleted)s.',
                        'removed %(name)s %(deleted)s.',
                        len(deleted)
                ) % {
                    'deleted': ', '.join(deleted),
                    'name': tag_name_pluralized
                }
            )
            short_comments.append(ungettext(
                        'removed %(count)i %(name)s.',
                        'removed %(count)i %(name)s.',
                        len(deleted)
                ) % {
                    'count': len(deleted),
                    'name': tag_name_pluralized
                }
            )
        if added:
            tag_name_pluralized = self.pluralize_tag(added)
            comments.append(ungettext(
                        'added %(name)s %(added)s.',
                        'added %(name)s %(added)s.',
                        len(added)
                ) % {
                    'added': ', '.join(added),
                    'name': tag_name_pluralized
                }
            )
            short_comments.append(ungettext(
                        'added %(count)i %(name)s.',
                        'added %(count)i %(name)s.',
                        len(added)
                ) % {
                    'count': len(added),
                    'name': tag_name_pluralized
                }
            )
        if not comments:
            return _('no changes made')
        comments = _(' and ').join(comments)
        # with lots of tags, this can get too long for db field
        if len(comments) > 140:
            return _(' and ').join(short_comments)
        return comments

    def merge(self, yours, theirs, ancestor):
        your_set = set([t.pk for t in yours['tags']])
        their_set = set(theirs['tags'])
        if ancestor:
            # merge based on original id, so get that for each historic tag
            old_pks = [t.id for t in Tag.versions.filter(
                                            history_id__in=ancestor['tags'])]
            old_set = set(old_pks)
        else:
            old_set = set()
        common = your_set.intersection(their_set)
        merged = your_set.union(their_set).difference(old_set).union(common)
        yours['tags'] = Tag.objects.filter(pk__in=merged)
        return yours
