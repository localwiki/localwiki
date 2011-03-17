""" Conversion of HTML into template with dynamic parts.

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
from urlparse import urlparse
from django.template import Node
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from pages.models import Page
from django.conf import settings


def sanitize_intermediate(html):
    """ Sanitizes template tags and escapes entities.
    """
    return html.replace('{', '&#123;')\
               .replace('}', '&#125;')\
               .replace('&', '{amp}')  # escape all entities


def sanitize_final(html):
    """ Fixes escaped entities.
    """
    return html.replace('{amp}', '&')  # unescape entities


def insert_text_before(text, elem):
    prev = elem.getprevious()
    if prev is not None:
        prev.tail = (prev.tail or '') + text
    else:
        elem.getparent().text = (elem.getparent().text or '') + text


def handle_link(elem):
    if not 'href' in elem.attrib:
        return

    href = elem.attrib['href']

    before = '{%% link "%s" %%}' % href + (elem.text or '')
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


def handle_image(elem):
    # only handle resized images
    if  not 'style' in elem.attrib:
        return

    src = elem.attrib['src'].replace(settings.MEDIA_URL, '')
    style = parse_style(elem.attrib['style'])
    if 'width' not in style or 'height' not in style:
        return
    width = int(style['width'].replace('px', ''))
    height = int(style['height'].replace('px', ''))

    before = '{%% thumbnail "%s" "%dx%d" as im %%}' % (src, width, height)
    after = '{% endthumbnail %}'

    elem.attrib['src'] = '{{ im.url }}'

    insert_text_before(before, elem)
    elem.tail = after + (elem.tail or '')
    return False


tag_imports = ['{% load pages_tags %}',
               '{% load thumbnail %}',
              ]


tag_handlers = {"a": [handle_link],
                "img": [handle_image],
               }


def html_to_template_text(unsafe_html):
    """
    Parse html and turn it into template text.
    """
    safe_html = sanitize_intermediate(unsafe_html)
    top_level_elements = fragments_fromstring(safe_html)

    # put top level elements in container
    container = etree.Element('div')
    if top_level_elements and not hasattr(top_level_elements[0], 'tag'):
        container.text = top_level_elements.pop(0)
    container.extend(top_level_elements)

    context = etree.iterwalk(container, events=('end',))
    # walk over all elements
    for action, elem in context:
        if not elem.tag in tag_handlers:
            continue
        for handler in tag_handlers[elem.tag]:
            can_continue = handler(elem)
            if can_continue is False:
                break

    template_bits = [etree.tostring(elem, encoding='utf-8')
                     for elem in container]
    return sanitize_final(''.join(tag_imports +
                                  [container.text or ''] +
                                  template_bits
                                  )
                         )


class LinkNode(Node):
    def __init__(self, href, nodelist):
        self.href = href
        self.nodelist = nodelist

    def render(self, context):
        try:
            url = self.href
            cls = ''
            url_parts = urlparse(url)
            #TODO: check if internal link, don't do anything if not
            if not url_parts.netloc:
                slug = slugify(url_parts.path)
                if not Page.objects.filter(slug__exact=slug).exists():
                    cls = ' class="missing_link"'
                else:
                    # want canonical url for existing pages
                    url = reverse('show-page', args=[slug])
            return '<a href="%s"%s>%s</a>' % (url, cls,
                                              self.nodelist.render(context))
        except:
            return ''
