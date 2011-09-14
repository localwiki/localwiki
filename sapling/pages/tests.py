# coding=utf-8

from urllib import quote

from django.test import TestCase
from django.db import models
from django import forms

from versionutils.merging.forms import MergeMixin
from forms import PageForm
from pages.models import Page, slugify, url_to_name, clean_name, name_to_url
from pages.plugins import html_to_template_text
from pages.plugins import tag_imports
from django.template.base import Template
from django.template.context import Context
from django.conf import settings


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
        self.old_allowed_src = settings.EMBED_ALLOWED_SRC
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
                    '<iframe src="http://www.youtube.com/embed/JVRsWAjvQSg"/>'
                    in rendered)
