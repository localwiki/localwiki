# coding=utf-8

from urllib import quote
from lxml.html import fragments_fromstring

from django.test import TestCase
from django.db import models
from django import forms
from django.template.base import Template
from django.template.context import Context
from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.gis.geos import GEOSGeometry

from versionutils.merging.forms import MergeMixin
from forms import PageForm
from redirects.models import Redirect
from maps.models import MapData

from pages.models import (Page, PageFile, slugify,
    url_to_name, clean_name, name_to_url)
from pages.plugins import html_to_template_text
from pages.plugins import tag_imports
from pages.xsstests import xss_exploits
from pages import exceptions


class PageTest(TestCase):
    def test_clean_name(self):
        self.assertEqual(clean_name(' Front Page '), 'Front Page')
        self.assertEqual(clean_name('_edit'), 'edit')
        self.assertEqual(clean_name('Front Page /_edit'), 'Front Page/edit')
        self.assertEqual(clean_name('/Front Page/'), 'Front Page')
        self.assertEqual(clean_name('Front Page// /'), 'Front Page')

    def test_url_to_name(self):
        self.assertEqual(url_to_name('Front_Page'), 'Front Page')
        self.assertEqual(url_to_name('Ben_%26_Jerry%27s'), "Ben & Jerry's")

    def test_name_to_url(self):
        self.assertEqual(name_to_url('Front Page'), 'Front_Page')
        self.assertEqual(name_to_url("Ben & Jerry's"), 'Ben_%26_Jerry%27s')

    def test_slugify(self):
        # spaces and casing
        self.assertEqual(slugify('Front Page'), 'front page')
        self.assertEqual(slugify('fRoNt PaGe'), 'front page')
        self.assertEqual(slugify('Front_Page'), 'front page')
        self.assertEqual(slugify('Front+Page'), 'front page')
        self.assertEqual(slugify('Front%20Page'), 'front page')

        # slashes
        self.assertEqual(slugify('Front Page/Talk'), 'front page/talk')
        self.assertEqual(slugify('Front Page%2FTalk'), 'front page/talk')

        # extra spaces
        self.assertEqual(slugify(' I  N  C  E  P  T  I  O  N '),
                                'i n c e p t i o n')

        # quotes and other stuff
        self.assertEqual(slugify("Ben & Jerry's"), "ben & jerry's")
        self.assertEqual(slugify("Ben & Jerry's"), "ben & jerry's")
        self.assertEqual(slugify("Ben_%26_Jerry's"), "ben & jerry's")
        self.assertEqual(slugify('Manny "Pac-Man" Pacquaio'),
                                'manny "pac-man" pacquaio')
        self.assertEqual(slugify("Where am I?"), "where am i")
        self.assertEqual(slugify("What the @#$!!"), "what the @$!!")

        # unicode
        self.assertEqual(slugify("Заглавная Страница".decode('utf-8')),
                         'заглавная страница'.decode('utf-8').lower())
        encoded = ("%D0%B7%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F"
                     "_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0")
        self.assertEqual(slugify(encoded),
                         'заглавная страница'.decode('utf-8'))
        self.assertEqual(slugify("Заглавная%20Страница".decode('utf-8')),
                         'заглавная страница'.decode('utf-8'))

        # idempotent?
        a = 'АЯ `~!@#$%^&*()-_+=/\|}{[]:;"\'<>.,'
        self.assertEqual(slugify(a), 'ая !@$%&*()- /"\'.,'.decode('utf-8'))
        self.assertEqual(slugify(a), slugify(slugify(a)))

    def test_pretty_slug(self):
        a = Page(name='Front Page')
        self.assertEqual(a.pretty_slug, 'Front_Page')
        a = Page(name='Front Page/Talk')
        self.assertEqual(a.pretty_slug, 'Front_Page/Talk')
        a = Page(name="Ben & Jerry's")
        self.assertEqual(a.pretty_slug, "Ben_%26_Jerry%27s")
        a = Page(name='Заглавная Страница')
        slug = ("%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F"
                "_%D0%A1%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0")
        assert slug == quote('Заглавная_Страница')
        self.assertEqual(a.pretty_slug, slug)

    def test_merge_conflict(self):
        p = Page()
        p.content = '<p>old content</p>'
        p.name = 'Front Page'
        p.save()

        a = PageForm(instance=p)
        b = PageForm(instance=p)
        b_post = b.initial
        b_post['content'] = '<p>b content</p>'
        b = PageForm(b_post, instance=p)
        self.failUnless(b.is_valid())
        b.save()

        p = Page.objects.get(pk=p.pk)
        a_post = a.initial
        a_post['content'] = '<p>a content</p>'
        a = PageForm(a_post, instance=p)
        self.failIf(a.is_valid())
        self.failUnless(PageForm.conflict_error in str(a.errors))

        a_post = a.data
        a = PageForm(a_post, instance=p)
        self.failUnless(a.is_valid())
        a.save()
        p = Page.objects.get(pk=p.pk)
        self.failUnless('Edit conflict!' in p.content)

    def test_page_rename(self):
        p = Page()
        p.content = "<p>The page content.</p>"
        p.name = "Original page"
        p.save()

        p.rename_to("New page")

        # Renamed-to page should exist.
        new_p = Page.objects.get(name="New page")
        # new_p should have the same content.
        self.assertEqual(new_p.content, p.content)

        # "Original page" should no longer exist.
        pgs = Page.objects.filter(name="Original page")
        self.assertEqual(len(pgs), 0)
        # and a redirect from "original page" to "New page" should exist.
        Redirect.objects.filter(source="original page", destination=new_p)

        ###########################################################
        # Renaming to a page that already exists should raise an
        # exception and not affect the original page.
        ###########################################################
        p = Page()
        p.content = "<p>Hello, world.</p>"
        p.name = "Page A"
        p.save()

        self.assertRaises(exceptions.PageExistsError, p.rename_to, "New page")
        # p should be unaffected.  No redirect should be created.
        p = Page.objects.get(name="Page A")
        self.assertEqual(p.content, "<p>Hello, world.</p>")
        self.assertEqual(len(Redirect.objects.filter(source="page a")), 0)

        ###########################################################
        # Renaming should carry along files and FK'ed items that
        # point to it.
        ###########################################################
        p = Page()
        p.content = "<p>A page with files and a map.</p>"
        p.name = "Page With FKs"
        p.save()
        # Create a file that points at the page.
        pf = PageFile(file=ContentFile("foo"), name="file.txt", slug=p.slug)
        pf.save()
        # Create a redirect that points at the page.
        redirect = Redirect(source="foobar", destination=p)
        redirect.save()
        # Create a map that points at the page.
        points = GEOSGeometry("""MULTIPOINT (-122.4378964233400069 37.7971758820830033, -122.3929211425700032 37.7688207875790027, -122.3908612060599950 37.7883584775320003, -122.4056240844700056 37.8013807351830025, -122.4148937988299934 37.8002956347170027, -122.4183270263600036 37.8051784612779969)""")
        map = MapData(points=points, page=p)
        map.save()

        p.rename_to("New Page With FKs")

        new_p = Page.objects.get(name="New Page With FKs")
        self.assertEqual(len(MapData.objects.filter(page=new_p)), 1)
        # Two redirects: one we created explicitly and one that was
        # created during rename_to()
        self.assertEqual(len(Redirect.objects.filter(destination=new_p)), 2)
        self.assertEqual(len(PageFile.objects.filter(slug=new_p.slug)), 1)

        # Renaming should keep slugs pointed at old page /and/ copy
        # them to the new page.
        self.assertEqual(len(PageFile.objects.filter(slug=p.slug)), 1)

        ###########################################################
        # Renaming with multiple files.
        ###########################################################
        p = Page()
        p.content = "<p>A new page with multiple files.</p>"
        p.name = "Page with multiple files"
        p.save()
        # Create a file that points at the page.
        pf = PageFile(file=ContentFile("foo"), name="file.txt", slug=p.slug)
        pf.save()
        pf = PageFile(file=ContentFile("foo2"), name="file2.txt", slug=p.slug)
        pf.save()
        pf = PageFile(file=ContentFile("foo3"), name="file3.txt", slug=p.slug)
        pf.save()
        p.rename_to("A page with multiple files 2")

        p = Page.objects.get(name="A page with multiple files 2")
        self.assertEqual(len(PageFile.objects.filter(slug=p.slug)), 3)

        ###########################################################
        # Reverting a renamed page should be possible and should
        # restore files and FK'ed items that were pointed at the
        # original page.  The renamed-to page should still exist
        # after the revert and should still have its own files and
        # FK'ed items pointed at it.
        ###########################################################
        p = Page(name="Page With FKs", slug="page with fks")
        # get the version right before it was deleted
        v_before_deleted = len(p.versions.all()) - 1
        p_h = p.versions.as_of(version=v_before_deleted)
        p_h.revert_to()
        p = Page.objects.get(name="Page With FKs")
        self.assertEqual(len(MapData.objects.filter(page=p)), 1)
        self.assertEqual(len(PageFile.objects.filter(slug=p.slug)), 1)

        p2 = Page.objects.get(name="New Page With FKs")
        self.assertEqual(len(MapData.objects.filter(page=p2)), 1)
        self.assertEqual(len(PageFile.objects.filter(slug=p2.slug)), 1)

        self.assertEqual(len(Redirect.objects.filter(destination=p2)), 1)

        ###########################################################
        # Renaming a page and then renaming it back.
        ###########################################################
        # 1. Simple case
        p = Page(name="Page X", content="<p>Foobar</p>")
        p.save()
        p.rename_to("Page Y")
        self.assertEqual(len(Page.objects.filter(name="Page X")), 0)
        self.assertEqual(len(Page.objects.filter(name="Page Y")), 1)

        p_new = Page.objects.get(name="Page Y")
        p_new.rename_to("Page X")
        self.assertEqual(len(Page.objects.filter(name="Page X")), 1)
        self.assertEqual(len(Page.objects.filter(name="Page Y")), 0)

        # 2. If we have FKs pointed at the page this shouldn't be
        # totally fucked.
        p = Page(name="Page X2", content="<p>Foo X</p>")
        p.save()
        points = GEOSGeometry("""MULTIPOINT (-122.4378964233400069 37.7971758820830033, -122.3929211425700032 37.7688207875790027, -122.3908612060599950 37.7883584775320003, -122.4056240844700056 37.8013807351830025, -122.4148937988299934 37.8002956347170027, -122.4183270263600036 37.8051784612779969)""")
        map = MapData(points=points, page=p)
        map.save()
        # Create a file that points at the page.
        pf = PageFile(file=ContentFile("foooo"), name="file_foo.txt", slug=p.slug)
        pf.save()

        p.rename_to("Page Y2")
        p_new = Page.objects.get(name="Page Y2")
        # FK points at the page we renamed to.
        self.assertEqual(len(MapData.objects.filter(page=p_new)), 1)
        self.assertEqual(len(PageFile.objects.filter(slug=p_new.slug)), 1)

        # Now rename it back.
        p_new.rename_to("Page X2")
        p = Page.objects.get(name="Page X2")
        # After rename-back-to, FK points to the renamed-back-to page.
        self.assertEqual(len(MapData.objects.filter(page=p)), 1)
        self.assertEqual(len(PageFile.objects.filter(slug=p.slug)), 1)

        ###########################################################
        # Renaming a page but keeping the same slug
        ###########################################################
        p = Page(name="Foo A", content="<p>Foo A</p>")
        p.save()
        p.rename_to("FOO A")

        # Name has changed.
        self.assertEqual(len(Page.objects.filter(name="FOO A")), 1)
        # Has the same history, with a new entry for the name change.
        p = Page.objects.get(name="FOO A")
        p1, p0 = p.versions.all()
        self.assertEqual(p1.name, 'FOO A')
        self.assertEqual(p0.name, 'Foo A')
        self.assertEqual(p0.content, p1.content)

        ###########################################################
        # Renaming a page twice (A -> B -> C) and then revert A to
        # an existing state.
        ###########################################################
        p = Page(name="Bar A", content="<p>Bar A</p>")
        p.save()
        p.rename_to("Bar B")
        p = Page.objects.get(name="Bar B")
        p.rename_to("Bar C")

        p = Page(name="Bar A", slug="bar a")
        p_h = p.versions.as_of(version=1)
        p_h.revert_to()

        ###########################################################
        # Renaming a page back and forth and reverting.
        ###########################################################
        p = Page(name="Zoo A", content="<p>Zoo A</p>")
        p.save()
        p.rename_to("Zoo B")
        p = Page.objects.get(name="Zoo B")
        p.rename_to("Zoo A")
        p = Page.objects.get(name="Zoo A")
        p.rename_to("Zoo B")

        p = Page(name="Zoo A", slug="zoo a")
        p_h = p.versions.as_of(version=1)
        p_h.revert_to()

        ###########################################################
        # page A, rename to B, then create new A, rename B to C,
        # rename C to B, then revert C to first version
        ###########################################################
        p = Page(name="Mike A", content="<p>A</p>")
        p.save()
        p.rename_to("Mike B")
        new_a = Page(name="Mike A", content="<p>A new</p>")
        new_a.save()
        p = Page.objects.get(name="Mike B")
        p.rename_to("Mike C")
        p = Page.objects.get(name="Mike C")
        p.rename_to("Mike B")

        p_c = Page(name="Mike C", slug="mike c")
        p_h = p_c.versions.as_of(version=1)
        p_h.revert_to()


class TestModel(models.Model):
    save_time = models.DateTimeField(auto_now=True)
    contents = models.TextField()


class TestForm(MergeMixin, forms.ModelForm):
    class Meta:
        model = TestModel


class TestMergeForm(MergeMixin, forms.ModelForm):
    class Meta:
        model = TestModel

    def merge(self, yours, theirs, ancestor):
        yours['contents'] += theirs['contents']
        return yours


class MergeModelFormTest(TestCase):
    def test_get_version_date(self):
        """
        Should return empty string or value of auto_now field
        """
        m = TestModel()
        m.contents = 'abc'
        f = TestForm(instance=m)
        # before save, should return empty string
        self.failUnless(f.get_version_date(m) == '')
        m.save()
        # after save, should return value of auto_now field
        self.failUnless(f.get_version_date(m) == m.save_time)

    def test_renders_version_date(self):
        """
        Should output current version in form
        """
        m = TestModel()
        m.contents = 'abc'
        m.save()
        f = TestForm(instance=m)
        self.failUnless(str(m.save_time) in f.as_table())

    def test_detects_conflict(self):
        """
        Should raise exception if the model object has been changed since
        form was created
        """
        m_old = TestModel()
        m_old.contents = 'old contents'
        m_old.save()
        # a and b get a form
        a = TestForm(instance=m_old)
        b = TestForm(instance=m_old)

        #b edits and posts
        b_post = b.initial
        b_post['contents'] = 'b contents'
        b = TestForm(b_post, instance=m_old)
        self.failUnless(b.is_valid())
        b.save()
        m_new = TestModel.objects.get(pk=m_old.pk)

        #a edits and posts
        a_post = a.initial
        a_post['contents'] = 'a contents'
        a = TestForm(a_post, instance=m_new)
        self.failIf(a.is_valid())
        self.failUnless(MergeMixin.conflict_error in str(a.errors))

        #repeated save with the same form rendered again should work, though
        a_post = a.data
        a = TestForm(a_post, instance=m_new)
        self.failUnless(a.is_valid())
        a.save()
        m_new = TestModel.objects.get(pk=m_old.pk)
        self.failUnless(m_new.contents == 'a contents')

    def test_detects_conflict_and_merges(self):
        """
        Should call merge() when there is a conflict
        """
        m_old = TestModel()
        m_old.contents = 'old contents'
        m_old.save()
        # a and b get a form
        a = TestMergeForm(instance=m_old)
        b = TestMergeForm(instance=m_old)

        #b edits and posts
        b_post = b.initial
        b_post['contents'] = 'def'
        b = TestMergeForm(b_post, instance=m_old)
        self.failUnless(b.is_valid())
        b.save()
        m_new = TestModel.objects.get(pk=m_old.pk)

        #a edits and posts
        a_post = a.initial
        a_post['contents'] = 'abc'
        a = TestMergeForm(a_post, instance=m_new)
        #this should pass because TestMergeForm will merge anything
        self.failUnless(a.is_valid())
        a.save()
        m_new = TestModel.objects.get(pk=m_old.pk)
        # merge() in this case concatenates the two versions
        self.failUnless(m_new.contents == 'abcdef')


class HTMLToTemplateTextTest(TestCase):
    def test_plaintext(self):
        html = "No XHTML"
        imports = ''.join(tag_imports)
        self.assertEqual(html_to_template_text(html), imports + "No XHTML")

    def test_django_tags_escaped(self):
        html = "<div>{% if 1 %}evil{% endif %}</div>"
        template_text = html_to_template_text(html)
        imports = ''.join(tag_imports)
        self.assertEqual(
            template_text,
            imports +
            "<div>&#123;% if 1 %&#125;evil&#123;% endif %&#125;</div>"
        )

        html = "<div>{{% if 1 %}}evil{{% endif %}}</div>"
        template_text = html_to_template_text(html)
        self.assertEqual(
            template_text,
            imports + (
            "<div>&#123;&#123;% if 1 %&#125;&#125;evil"
             "&#123;&#123;% endif %&#125;&#125;</div>")
        )

        # malicious use of intermediate sanitization
        html = "<div>{amp}</div>"
        template_text = html_to_template_text(html)
        self.assertEqual(
            template_text,
            imports + (
            "<div>&#123;amp&#125;</div>")
        )

        # preserves entities
        html = '<div>&amp;&lt; then &#123;</div>'
        template_text = html_to_template_text(html)
        self.assertEqual(
            template_text,
            imports + (
            "<div>&amp;&lt; then &#123;</div>")
        )

    def test_link_tag(self):
        html = '<div><a href="http://example.org"></a></div>'
        template_text = html_to_template_text(html)
        imports = ''.join(tag_imports)
        self.assertEqual(template_text,
            imports +
            '<div>{% link "http://example.org" %}{% endlink %}</div>')

        html = '<div><a href="http://example.org">hi!</a></div>'
        template_text = html_to_template_text(html)
        self.assertEqual(template_text,
            imports +
            '<div>{% link "http://example.org" %}hi!{% endlink %}</div>')

        html = '<div><a href="http://example.org">hi!</a></div>'
        template_text = html_to_template_text(html)
        self.assertEqual(template_text,
            imports +
            '<div>{% link "http://example.org" %}hi!{% endlink %}</div>')


class PluginTest(TestCase):
    def setUp(self):
        self.old_allowed_src = getattr(settings, 'EMBED_ALLOWED_SRC', ['.*'])
        settings.EMBED_ALLOWED_SRC = ['http://www.youtube.com/embed/.*',
                                     'http://player.vimeo.com/video/.*']

    def tearDown(self):
        settings.EMBED_ALLOWED_SRC = self.old_allowed_src

    def test_include_tag(self):
        html = '<a class="plugin includepage" href="Front_Page">Front Page</a>'
        template_text = html_to_template_text(html)
        imports = ''.join(tag_imports)
        self.assertEqual(template_text,
                         imports + ('<div>{% include_page "Front_Page" %}'
                                    '</div>'))

    def test_include_plugin(self):
        a = Page(name='Front Page')
        a.content = '<a class="plugin includepage" href="Explore">dummy</a>'
        a.save()

        b = Page(name='Explore')
        b.content = '<p>Some text</p>'
        b.save()

        context = Context({'page': a})
        template = Template(html_to_template_text(a.content, context))
        html = template.render(context)
        self.assertEqual(html,
                    '<div><p>Some text</p></div>')

    def test_include_showtitle(self):
        a = Page(name='Front Page')
        a.content = ('<a class="plugin includepage includepage_showtitle"'
                     ' href="Explore">dummy</a>')
        a.save()

        b = Page(name='Explore')
        b.content = '<p>Some text</p>'
        b.save()

        context = Context({'page': a})
        template = Template(html_to_template_text(a.content, context))
        html = template.render(context)
        self.assertEqual(html,
                    ('<div><h2><a href="/Explore">Explore</a></h2>'
                     '<p>Some text</p></div>'))

    def test_include_left(self):
        a = Page(name='Front Page')
        a.content = ('<a class="plugin includepage includepage_left"'
                     ' href="Explore">dummy</a>')
        a.save()

        b = Page(name='Explore')
        b.content = '<p>Some text</p>'
        b.save()

        context = Context({'page': a})
        template = Template(html_to_template_text(a.content, context))
        html = template.render(context)
        self.assertEqual(html,
                    '<div class="includepage_left"><p>Some text</p></div>')

    def test_include_width(self):
        a = Page(name='Front Page')
        a.content = ('<a class="plugin includepage" style="width: 100px"'
                     ' href="Explore">dummy</a>')
        a.save()

        b = Page(name='Explore')
        b.content = '<p>Some text</p>'
        b.save()

        context = Context({'page': a})
        template = Template(html_to_template_text(a.content, context))
        html = template.render(context)
        self.assertEqual(html,
                    ('<div style="width: 100px;">'
                     '<p>Some text</p></div>'))

    def test_include_nonexistant(self):
        """ Should give an error message when including nonexistant page
        """
        a = Page(name='Front Page')
        a.content = '<a class="plugin includepage" href="New page">dummy</a>'
        a.save()
        context = Context({'page': a})
        template = Template(html_to_template_text(a.content, context))
        html = template.render(context)
        self.failUnless(('Unable to include <a href="/New_page"'
                         ' class="missing_link">New page</a>') in html)

    def test_endless_include(self):
        """ Should detect endless loops and give an error message
        """
        a = Page(name='Front Page')
        a.content = '<a class="plugin includepage" href="Front_Page">dummy</a>'
        a.save()
        context = Context({'page': a})
        template = Template(html_to_template_text(a.content, context))
        html = template.render(context)
        self.failUnless(('Unable to include <a href="/Front_Page">Front Page'
                         '</a>: endless include loop') in html)

    def test_double_include(self):
        """ Multiple includes are ok
        """
        a = Page(name='Front Page')
        a.content = ('<a class="plugin includepage" href="Explore">dummy</a>'
                     '<a class="plugin includepage" href="Explore">dummy</a>')
        a.save()

        b = Page(name='Explore')
        b.content = '<p>Some text</p>'
        b.save()

        context = Context({'page': a})
        template = Template(html_to_template_text(a.content, context))
        html = template.render(context)
        self.assertEqual(html,
            ('<div><p>Some text</p></div><div><p>Some text</p></div>'))

    def test_embed_tag(self):
        html = ('<span class="plugin embed">&lt;strong&gt;Hello&lt;/strong&gt;'
                '</span>')
        template_text = html_to_template_text(html)
        imports = ''.join(tag_imports)
        self.assertEqual(template_text,
                         imports + ('{% embed_code %} &lt;strong&gt;Hello&lt;'
                                    '/strong&gt; {% endembed_code %}'))

    def test_embed_whitelist_reject(self):
        html = ('<span class="plugin embed">&lt;iframe src="http://evil.com"'
                '&gt;&lt;/iframe&gt;</span>')
        template = Template(html_to_template_text(html))
        rendered = template.render(Context())
        self.failUnless(('The embedded URL is not on the list of approved '
                         'providers') in rendered)

    def test_embed_whitelist_accept(self):
        html = ('<span class="plugin embed">&lt;iframe '
                'src="http://www.youtube.com/embed/JVRsWAjvQSg"'
                '&gt;&lt;/iframe&gt;</span>')
        template = Template(html_to_template_text(html))
        rendered = template.render(Context())
        self.failUnless(
            '<iframe src="http://www.youtube.com/embed/JVRsWAjvQSg"></iframe>'
            in rendered)


class XSSTest(TestCase):
    """ Test for tricky attempts to inject scripts into a page
    Exploits adapted from http://ha.ckers.org/xss.html
    """
    def encode_hex_entities(self, string):
        return''.join('&#x%02X;' % ord(c) for c in string)

    def encode_decimal_entities(self, string):
        return''.join('&#%i' % ord(c) for c in string)

    def test_encode_hex_entities(self):
        encoded = self.encode_hex_entities('\'\';!--"<XSS>=&{()}')
        self.assertEqual(encoded, '&#x27;&#x27;&#x3B;&#x21;&#x2D;&#x2D;&#x22;'
                                  '&#x3C;&#x58;&#x53;&#x53;&#x3E;&#x3D;&#x26;'
                                  '&#x7B;&#x28;&#x29;&#x7D;')

    def test_encode_decimal_entities(self):
        encoded = self.encode_decimal_entities('\'\';!--"<XSS>=&{()}')
        self.assertEqual(encoded, '&#39&#39&#59&#33&#45&#45&#34&#60&#88&#83'
                         '&#83&#62&#61&#38&#123&#40&#41&#125')

    def test_xss_all(self):
        for exploit in xss_exploits:
            for e in [exploit, exploit.lower(), exploit.upper()]:
                self.failIf(self.is_exploitable(e), 'XSS exploit: ' + e)
                hex = self.encode_hex_entities(e)
                self.failIf(self.is_exploitable(hex), 'XSS exploit hex: ' + e)
                dec = self.encode_decimal_entities(e)
                self.failIf(self.is_exploitable(dec), 'XSS exploit dec: ' + e)

    def is_exploitable(self, exploit):
        p = Page(name='XSS Test', content=exploit)
        p.clean_fields()
        t = Template(html_to_template_text(p.content))
        html = t.render(Context())
        return self.contains_script(html)

    def contains_script(self, html):
        fragments = fragments_fromstring(html)
        for frag in fragments:
            if not hasattr(frag, 'tag'):
                continue
            for e in frag.iter():
                if e.tag.lower() == 'script' or e.tag.lower() == 'xss':
                    return True
                for a, v in e.attrib.items():
                    if a.lower().startswith('on'):
                        # event handler
                        return True
                    if v.lower().startswith('jav'):
                        # script protocol
                        return True
        return False
