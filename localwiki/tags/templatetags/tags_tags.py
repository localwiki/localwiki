from copy import copy

from django import template
from django.template.loader import render_to_string

from pages.templatetags.pages_tags import IncludeContentNode
from regions.models import Region

from tags.models import PageTagSet, slugify, Tag
from tags.forms import PageTagSetForm
from tags.views import TaggedList


register = template.Library()


@register.simple_tag(takes_context=True)
def page_tags(context, page):
    try:
        tag_list = page.pagetagset.tags.all()
    except PageTagSet.DoesNotExist:
        tag_list = []
    context['tag_list'] = tag_list
    return render_to_string('tags/tag_list_snippet.html', context)


@register.simple_tag(takes_context=True)
def page_tags_form(context, page):
    try:
        tags = page.pagetagset
    except PageTagSet.DoesNotExist:
        tags = PageTagSet(page=page, region=page.region)
    context.push()
    context['form'] = PageTagSetForm(instance=tags, region=page.region)
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

    def get_title(self, context):
        return 'Pages tagged &ldquo;%s&rdquo;' % self.name

    def get_content(self, context):
        region = context['region']
        try:
            self.tag = Tag.objects.get(slug=slugify(self.name), region=region)
        except Tag.DoesNotExist:
            self.tag = None

        view = TaggedList()
        view.kwargs = dict(slug=self.name, region=region.slug)
        view.request = context['request']
        view.object_list = view.get_queryset()

        context = copy(context)
        context.update(view.get_context_data(object_list=view.object_list))
        return render_to_string('tags/tagged_list_snippet.html', context)
