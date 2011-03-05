import os
from lxml import etree
from lxml.html import fragments_fromstring
from urlparse import urlparse
from django.template import Node
from django.template.base import Template
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from pages.models import Page
from django.conf import settings


def sanitize_template_tags(html):
    return html.replace('{', '&#123;').replace('}', '&#125;')

def template_tag(tag_text):
    return '{%% %s %%}' % (tag_text,)

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
    
    before = template_tag('link "%s"' % href) + (elem.text or '')
    after =  template_tag('endlink') + (elem.tail or '')
    
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
    width = int(style['width'].replace('px',''))
    height = int(style['height'].replace('px',''))
    
    before = template_tag('thumbnail "%s" "%dx%d" as im' % (src, width, height))
    after = template_tag('endthumbnail')
    
    elem.attrib['src'] = '{{ im.url }}'
    
    insert_text_before(before, elem)
    elem.tail = after + (elem.tail or '')
    return False

tag_imports = ['{% load pages_tags %}',
               '{% load thumbnail %}',
              ]

tag_handlers = { "a" : [handle_link],
                 "img" : [handle_image],
               }
    
def html_to_template(unsafe_html):
    """ Parse html and turn it into a template
    """
    safe_html = sanitize_template_tags(unsafe_html)
    top_level_elements = fragments_fromstring(safe_html.decode('utf-8'))
    
    # put top level elements in container
    container = etree.Element('div')
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
    
    template_bits = [etree.tostring(elem, encoding='utf-8') for elem in container]
    return Template(''.join(tag_imports + template_bits))

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
            return '<a href="%s"%s>%s</a>' % (url, cls, self.nodelist.render(context))
        except:
            return ''