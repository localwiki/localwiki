"""
Conversion of HTML into template with dynamic parts.

We want to allow some dynamic content that gets inserted as the HTML is
rendered. This is done by converting certain HTML tags into template tags.

For example, to mark links to non-existant pages with a different style, this:
    <a href="My Page">My Page</a>
gets converted to this:
    {% link "My Page" %}My Page{% endlink %}
and rendered as appropriate by the LinkNode class.

The function html_to_template_text parses the HTML and lets each registered
handler a chance to do something with an element, such as replace it with a
template tag.
"""
from lxml import etree
from lxml.html import fragments_fromstring
from xml.sax.saxutils import escape
from HTMLParser import HTMLParser
from urllib import unquote_plus
from urlparse import urlparse

from django.template import Node
from django.core.urlresolvers import reverse

from pages.models import Page, name_to_url, url_to_name, PageFile
from pages.models import slugify


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
    fragment = _unescape_util.unescape(fragment)
    return sanitize_intermediate(fragment)


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


def insert_text_before(text, elem):
    prev = elem.getprevious()
    if prev is not None:
        prev.tail = (prev.tail or '') + text
    else:
        elem.getparent().text = (elem.getparent().text or '') + text


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


def parse_style(css):
    style = {}
    for line in css.split(';'):
        try:
            bits = line.split(':')
            style[bits[0].strip()] = bits[1].strip()
        except:
            pass
    return style


_files_url = '_files/'


def file_url_to_name(url):
    return unquote_plus(url.replace(_files_url, '').encode('utf-8'))


def handle_image(elem, context=None):
    # only handle resized images
    do_thumbnail = True
    style = parse_style(elem.attrib.get('style', ''))
    if 'width' not in style or 'height' not in style:
        do_thumbnail = False

    src = elem.attrib['src']
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
        elem.attrib['src'] = '{{ im.url }}'
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
              ]


tag_handlers = {"a": [handle_link],
                "img": [handle_image],
               }


def html_to_template_text(unsafe_html, context=None):
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
        if not elem.tag in tag_handlers:
            continue
        for handler in tag_handlers[elem.tag]:
            can_continue = handler(elem, context)
            if can_continue is False:
                break

    template_bits = [etree.tostring(elem, encoding='UTF-8')
                     for elem in container]
    return sanitize_final(''.join(tag_imports +
                                  [escape(container.text or '')] +
                                  template_bits
                                  )
                         )


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
                    print "URL", url
                    filename = file_url_to_name(url)
                    print "FILENAME", filename
                    url = reverse('pages:file-info', args=[page.pretty_slug,
                                                       filename])
                    try:
                        file = PageFile.objects.get(slug__exact=page.slug,
                                                    name__exact=filename)
                        cls = ' class="file_%s"' % file.rough_type
                    except PageFile.DoesNotExist:
                        cls = ' class="missing_link"'
                else:
                    try:
                        page = Page.objects.get(slug__exact=slugify(url))
                        url = reverse('pages:show', args=[page.pretty_slug])
                    except Page.DoesNotExist:
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
