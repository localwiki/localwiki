from django import template
from django.template.loader_tags import BaseIncludeNode
from django.template import Template
from django.conf import settings

from pages.plugins import html_to_template_text
from pages.plugins import LinkNode
from pages import models
from django.utils.text import unescape_string_literal
from pages.models import Page, slugify, url_to_name

register = template.Library()


@register.filter
def name_to_url(value):
    return models.name_to_url(value)
name_to_url.is_safe = True


class PageContentNode(BaseIncludeNode):
    def __init__(self, html_var, *args, **kwargs):
        super(PageContentNode, self).__init__(*args, **kwargs)
        self.html_var = template.Variable(html_var)

    def render(self, context):
        try:
            html = unicode(self.html_var.resolve(context))
            t = Template(html_to_template_text(html, context))
            return self.render_template(t, context)
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''


class IncludePageNode(BaseIncludeNode):
    def __init__(self, page_name, *args, **kwargs):
        super(IncludePageNode, self).__init__(*args, **kwargs)
        self.page_name = url_to_name(page_name)

    def render(self, context):
        try:
            try:
                page = Page.objects.get(slug__exact=slugify(self.page_name))
                content = '<h2><a href="%s">%s</a></h2>' % (page.pretty_slug,
                                                            page.name)
                content = content + page.content
            except Page.DoesNotExist:
                content = ('<p class="plugin includepage">Unable to include '
                           '<a href="%s">%s</a></p>'
                           % (self.page_name, self.page_name))
            template = Template(html_to_template_text(content))
            return self.render_template(template, context)
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''


@register.tag(name='render_page')
def do_render_page(parser, token):
    try:
        tag, html_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, ("%r tag requires one argument" %
                                             token.contents.split()[0])
    return PageContentNode(html_var)


@register.tag(name='include_page')
def do_include_page(parser, token):
    try:
        tag, page_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, ("%r tag requires one argument" %
                                             token.contents.split()[0])
    if is_quoted(page_name):
        page_name = unescape_string_literal(page_name)
    return IncludePageNode(page_name)


def is_quoted(text):
    return text[0] == text[-1] and text[0] in ('"', "'")


@register.tag(name='link')
def do_link(parser, token):
    try:
        tag, href = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires one argument" %
                                           token.contents.split()[0])
    if not is_quoted(href):
        raise template.TemplateSyntaxError(
                                    "%r tag's argument should be in quotes" %
                                     token.contents.split()[0])

    nodelist = parser.parse(('endlink',))
    parser.delete_first_token()
    return LinkNode(unescape_string_literal(href), nodelist)
