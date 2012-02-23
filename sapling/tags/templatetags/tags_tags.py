from django import template
from tags.models import PageTagSet
from tags.forms import PageTagSetForm
from django.template.loader import render_to_string

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


