from django import template
from tags.models import PageTagSet, slugify, Tag
from tags.forms import PageTagSetForm
from django.template.loader import render_to_string
from pages.templatetags.pages_tags import IncludeContentNode
from tags.views import TaggedList


register = template.Library()


@register.simple_tag
def page_tags(page):
    try:
        tag_list = page.pagetagset.tags.all()
    except PageTagSet.DoesNotExist:
        tag_list = []
    return render_to_string('tags/tag_list_snippet.html',
                            {'tag_list': tag_list})


@register.simple_tag(takes_context=True)
def page_tags_form(context, page):
    try:
        tags = page.pagetagset
    except PageTagSet.DoesNotExist:
        tags = PageTagSet(page=page)
    context.push()
    context['form'] = PageTagSetForm(instance=tags)
    rendered = render_to_string('tags/pagetagset_form_snippet.html', context)
    context.pop()
    return rendered


@register.simple_tag
def page_tags_form_media():
    f = PageTagSetForm()
    return f.media


@register.tag(name='include_tag')
def do_include_page(parser, token):
    return IncludeTagNode(parser, token)


class IncludeTagNode(IncludeContentNode):
    def __init__(self, *args, **kwargs):
        super(IncludeTagNode, self).__init__(*args, **kwargs)
        try:
            self.tag = Tag.objects.get(slug=slugify(self.name))
        except Tag.DoesNotExist:
            self.tag = None

    def get_title(self, context):
        return 'Pages tagged &ldquo;%s&rdquo;' % self.name

    def get_content(self, context):
        view = TaggedList()
        view.kwargs = dict(slug=self.name)
        view.object_list = view.get_queryset()
        data = view.get_context_data(object_list=view.object_list)
        return render_to_string('tags/tagged_list_snippet.html', data)
