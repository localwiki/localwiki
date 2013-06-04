"""
Conversion of HTML into template with dynamic parts.

We want to allow some dynamic content that gets inserted as the HTML is
rendered. This is done by converting certain HTML tags into template tags.
There are two mechanisms to do this: plugin handlers and tag handlers.

Plugins are meant for inserting bits of dynamic content at specific places on
the final rendered page marked by a placeholder element. The output can be
whatever you like: widgets, bits of JavaScript, anything. Tag handlers, on the
other hand, are meant for fixing up the HTML slightly and transparently, i.e.,
fixing links and adding helpful visual styles and the like. When in doubt, use
plugins.

Plugin handlers work with HTML elements that have the class "plugin". When
an element has the class "plugin", it will be passed to registered handlers
based on the other classes it has.

For example, the following element will be passed to the handler registered for
the "includepage" class:

<a href="Navigation" class="plugin includepage">Include Navigation</a>

which will convert it to this:

{% include_page "Navigation %}

to be rendered by the include_page template tag.

Tag handlers work similarly, but they are applied by element tag instead of by
class.  They are best used for routine processing of content, such as styling.

For example, to mark links to non-existant pages with a different style, this:
    <a href="My Page">My Page</a>
gets converted to this:
    {% link "My Page" %}My Page{% endlink %}
and rendered as appropriate by the LinkNode class.

The function html_to_template_text parses the HTML and lets each registered
handler a chance to do something with an element, such as replace it with a
template tag.
"""
import re
from lxml import etree
from lxml.html import fragments_fromstring
from xml.sax.saxutils import escape
from HTMLParser import HTMLParser
from urllib import unquote_plus
from urlparse import urlparse
from copy import copy

from django.template import Node
from django.core.urlresolvers import reverse
from django.utils.text import unescape_entities
from django.utils.translation import  ugettext as _
from django.conf import settings

from ckeditor.models import parse_style, sanitize_html_fragment
from redirects.models import Redirect

from models import Page, name_to_url, url_to_name, PageFile
from models import allowed_tags as pages_allowed_tags
from models import allowed_attributes_map as pages_allowed_attributes_map
from models import allowed_styles_map as pages_allowed_styles_map
from models import slugify
from exceptions import IFrameSrcNotApproved


def sanitize_intermediate(html):
    """
    Sanitizes template tags and escapes entities.
    """
    return html.replace('{', '&#123;')\
               .replace('}', '&#125;')\
               .replace('&', '{amp}')  # escape all entities


_unescape_util = HTMLParser()


def desanitize(fragment):
    """
    Undo sanitization, when we need the original contents.
    """
    fragment = sanitize_final(fragment)
    return _unescape_util.unescape(fragment)


def sanitize_final(html):
    """
    Fixes escaped entities.
    """
    return html.replace('{amp}', '&')  # unescape entities


def escape_quotes(s):
    """
    Escapes double quotes for use in template tags.
    """
    return s.replace('"', '\\"')


def unquote_url(url):
    return unquote_plus(url.encode('utf-8'))


def prefixed_url_to_name(url, prefix):
    return unquote_url(url.replace(prefix, ''))


def insert_text_before(text, elem):
    prev = elem.getprevious()
    if prev is not None:
        prev.tail = (prev.tail or '') + text
    else:
        elem.getparent().text = (elem.getparent().text or '') + text


def include_content(elem, plugin_tag, context=None):
    href = elem.attrib['href']
    args = []
    if 'class' in elem.attrib:
        classes = elem.attrib['class'].split()
        args = [c[len('includepage_'):] for c in classes
                    if c.startswith('includepage_')]
    args = ['"%s"' % escape_quotes(href)] + args
    container = etree.Element('div')
    container.attrib['class'] = 'included_page_wrapper'
    align = [a for a in args if a in ['left', 'right']]
    if len(align):
        container.attrib['class'] += ' includepage_' + align[0]
    style = parse_style(elem.attrib.get('style', ''))
    if 'width' in style:
        container.attrib['style'] = 'width: ' + style['width'] + ';'
    tag_text = '{%% %s %s %%}' % (plugin_tag, ' '.join(args))
    container.text = tag_text
    elem.addprevious(container)
    elem.getparent().remove(elem)


def include_tag(elem, context=None):
    if not 'href' in elem.attrib:
        return
    href = unquote_url(desanitize(elem.attrib['href']))
    elem.attrib['href'] = prefixed_url_to_name(
        href.decode('utf-8'), 'tags/'
    ).decode('utf-8')
    return include_content(elem, 'include_tag', context)


def include_page(elem, context=None):
    if not 'href' in elem.attrib:
        return
    elem.attrib['href'] = unquote_url(
        desanitize(elem.attrib['href'])
    ).decode('utf-8')
    if elem.attrib['href'].startswith('tags/'):
        return include_tag(elem, context)
    return include_content(elem, 'include_page', context)


def embed_code(elem, context=None):
    before = '{%% embed_code %%} %s {%% endembed_code %%}' % elem.text
    insert_text_before(before, elem)
    elem.getparent().remove(elem)


def searchbox(elem, context=None):
    value = elem.attrib.get('value', '')
    before = '{%% searchbox "%s" %%} %s' % (value,
                                            elem.tail or '')
    insert_text_before(before, elem)
    elem.getparent().remove(elem)


def handle_link(elem, context=None):
    if not 'href' in elem.attrib:
        return

    href = desanitize(elem.attrib['href'])

    before = '{%% link "%s" %%}' % escape_quotes(href) + (elem.text or '')
    after = '{% endlink %}' + (elem.tail or '')

    insert_text_before(before, elem)
    for child in elem:
        elem.addprevious(child)
    insert_text_before(after, elem)

    elem.getparent().remove(elem)
    return False


_files_url = '_files/'


def file_url_to_name(url):
    return prefixed_url_to_name(url, _files_url)


def handle_image(elem, context=None):
    # only handle resized images
    do_thumbnail = True
    style = parse_style(elem.attrib.get('style', ''))
    if 'width' not in style or 'height' not in style:
        do_thumbnail = False

    src = desanitize(elem.attrib.get('src', ''))
    if not src.startswith(_files_url):
        return

    if not context or 'page' not in context:
        return

    page = context['page']
    try:
        file = PageFile.objects.get(slug__exact=page.slug,
                                     name__exact=file_url_to_name(src))
    except PageFile.DoesNotExist:
        return

    if do_thumbnail:
        width = int(style['width'].replace('px', ''))
        height = int(style['height'].replace('px', ''))
        escaped_filename = escape_quotes(file.file.name)
        before = '{%% thumbnail "%s" "%dx%d" as im %%}' % (escaped_filename,
                                                           width, height)
        after = '{% endthumbnail %}'
        # HTML will want to encode {{ }} inside a src, and we don't want that,
        # so we will just rename it to src_thumb until just before it's output
        del elem.attrib['src']
        elem.attrib['src_thumb'] = '{{ im.url }}'
        insert_text_before(before, elem)
        elem.tail = after + (elem.tail or '')
    else:
        elem.attrib['src'] = file.file.url
    info_url = reverse('pages:file-info', args=[page.pretty_slug,
                                                    file.name])
    link = etree.Element('a')
    link.attrib['href'] = info_url
    elem.addprevious(link)
    elem.getparent().remove(elem)
    link.append(elem)
    return False


tag_imports = ['{% load pages_tags %}',
               '{% load thumbnail %}',
               '{% load tags_tags %}',
              ]


tag_handlers = {"a": [handle_link],
                "img": [handle_image],
               }


plugin_handlers = {"includepage": include_page,
                   "includetag": include_tag,
                   "embed": embed_code,
                   "searchbox": searchbox,
                  }


def html_to_template_text(unsafe_html, context=None, render_plugins=True):
    """
    Parse html and turn it into template text.
    """
    # TODO: factor out parsing/serializing
    safe_html = sanitize_intermediate(unsafe_html)
    top_level_elements = fragments_fromstring(safe_html)

    # put top level elements in container
    container = etree.Element('div')
    if top_level_elements and not hasattr(top_level_elements[0], 'tag'):
        container.text = top_level_elements.pop(0)
    container.extend(top_level_elements)

    tree = etree.iterwalk(container, events=('end',))
    # walk over all elements
    for action, elem in tree:
        if 'class' in elem.attrib:
            classes = elem.attrib['class'].split()
            if 'plugin' in classes and render_plugins:
                for p in classes:
                    if p in plugin_handlers:
                        try:
                            plugin_handlers[p](elem, context)
                        except:
                            pass
                continue
        if not elem.tag in tag_handlers:
            continue
        for handler in tag_handlers[elem.tag]:
            try:
                can_continue = handler(elem, context)
                if can_continue is False:
                    break
            except:
                pass

    template_bits = [etree.tostring(elem, method='html', encoding='UTF-8')
                     for elem in container]
    container_text = escape(container.text or '').encode('UTF-8')
    template_text = sanitize_final(''.join(
        tag_imports + [container_text] + template_bits))
    # Restore img src for thumbnails
    template_text = template_text.replace('src_thumb', 'src')
    return template_text.decode('utf-8')


class LinkNode(Node):
    def __init__(self, href, nodelist):
        self.href = href
        self.nodelist = nodelist

    def render(self, context):
        try:
            cls = ''
            url = self.href
            page = context['page']
            if self.is_relative_link(url):
                if url.startswith('_files/'):
                    filename = file_url_to_name(url)
                    url = reverse('pages:file-info', args=[page.pretty_slug,
                                                       filename])
                    try:
                        file = PageFile.objects.get(slug__exact=page.slug,
                                                    name__exact=filename)
                        cls = ' class="file_%s"' % file.rough_type
                    except PageFile.DoesNotExist:
                        cls = ' class="missing_link"'
                elif unquote_plus(url).startswith('tags/'):
                    cls = ' class="tag_link"'
                else:
                    try:
                        page = Page.objects.get(slug__exact=slugify(url))
                        url = reverse('pages:show', args=[page.pretty_slug])
                    except Page.DoesNotExist:
                        # Check if Redirect exists.
                        if not Redirect.objects.filter(source=slugify(url)):
                            cls = ' class="missing_link"'
                        # Convert to proper URL: My%20page -> My_page
                        url = name_to_url(url_to_name(url))
                        url = reverse('pages:show', args=[url])
            return '<a href="%s"%s>%s</a>' % (url, cls,
                                              self.nodelist.render(context))
        except:
            return ''

    def is_relative_link(self, url):
        url_parts = urlparse(url)
        return (not url_parts.scheme and not url_parts.netloc
                and not url_parts.fragment)


class EmbedCodeNode(Node):
    allowed_tags = copy(pages_allowed_tags)
    allowed_attributes = copy(pages_allowed_attributes_map)
    allowed_styles_map = copy(pages_allowed_styles_map)

    # We allow the iframe tag in embeds.
    allowed_tags.append('iframe')
    allowed_attributes['iframe'] = [
        'allowfullscreen', 'width', 'height', 'src', 'style']
    allowed_styles_map['iframe'] = ['width', 'height']

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def sanitize(self, html):
        return sanitize_html_fragment(html, self.allowed_tags,
            self.allowed_attributes, self.allowed_styles_map)

    def _process_iframe(self, iframe):
        src = iframe.attrib.get('src', '')
        allowed_src = getattr(settings, 'EMBED_ALLOWED_SRC', ['.*'])
        # We don't want a self-closing iframe tag.
        if iframe.text is None:
            iframe.text = ''
        if any(re.match(regex, src) for regex in allowed_src):
            return iframe
        else:
            raise IFrameSrcNotApproved

    def render(self, context):
        try:
            html = unescape_entities(self.nodelist.render(context))
            safe_html = self.sanitize(html)
            top_level_elements = fragments_fromstring(safe_html)
            # TODO: We need to remember to patch in whatever pre-save
            #       HTML processing we eventually do here, too.  E.g.
            #       a spam URL blacklist.
            out = []
            for elem in top_level_elements:
                if elem.tag == 'iframe':
                    elem = self._process_iframe(elem)
                out.append(etree.tostring(elem, method='html',
                                          encoding='UTF-8'))
            return ''.join(out)

        except IFrameSrcNotApproved:
            return (
                '<span class="plugin embed">' +
                _('The embedded URL is not on the list of approved providers.  '
                'Contact the site administrator to add it.') +
                '</span>')
        except:
            return '<span class="plugin embed">' + _('Invalid embed code') + '</span>'


class SearchBoxNode(Node):
    def __init__(self, query=None):
        self.query = query

    def render(self, context):
        try:
            # TODO: put the JS in an external file, import via Media object
            html = ('<span class="searchbox">'
                    '<input type="text" name="q" value="%s">'
                    '<input type="submit" value="' + _('Search or create page') + '">'
                    '<script>$(function(){'
                    '$(".searchbox input[name=\'q\']").keypress(function(evt){'
                    'if(evt.which == 13)'
                    '$(".searchbox input[type=\'submit\']").click();});'
                    '$(".searchbox input[type=\'submit\']").click(function(){'
                    '  $("#header .site_search input[name=\'q\']").val('
                    '    $(this).parent().children("input[name=\'q\']").val()'
                    '  ).closest("form").submit();'
                    '})});</script>'
                    '</span>') % escape(self.query).encode('UTF-8')
            return html
        except Exception, e:
            return e
