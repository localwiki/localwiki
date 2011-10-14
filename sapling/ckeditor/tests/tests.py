# coding=utf-8

import os

from django.test import TestCase
from django.db import models
from django.core import exceptions

from ckeditor.models import XHTMLField
from ckeditor.models import XMLField
from ckeditor.models import HTML5Field
from ckeditor.models import HTML5FragmentField
from ckeditor.widgets import CKEditor


class XHTMLModel(models.Model):
    html = XHTMLField()


class HTML5Model(models.Model):
    html = HTML5Field()


class HTML5FragmentModel(models.Model):
    html = HTML5FragmentField()


class RestrictedHTML5FragmentModel(models.Model):
    html = HTML5FragmentField(allowed_elements=['a', 'span'],
                              allowed_attributes_map={'a': ['href'],
                                                      'span': ['style']},
                              allowed_styles_map={'span': ['width']})


class XHTMLFieldTest(TestCase):
    def test_html_schema_set(self):
        html = XHTMLField()
        self.assertTrue(isinstance(html, XMLField))
        self.assertEquals(html.schema_path, XHTMLField.schema_path)

    def test_html_schema_exists(self):
        self.assertTrue(os.path.exists(XHTMLField.schema_path))

    def test_valid_html(self):
        m = XHTMLModel()
        m.html = ('<html><head><title>Lorem</title></head>'
                  '<body>Ipsum</body></html>')
        m.clean_fields()

    def test_invalid_html(self):
        m = XHTMLModel()
        m.html = 'invalid html'
        self.assertRaises(exceptions.ValidationError, m.clean_fields)


class HTML5FieldTest(TestCase):
    def test_sanitize(self):
        m = HTML5Model()
        m.html = '<html><head/><body><script/></body></html>'
        m.clean_fields()
        self.assertEquals(m.html,
            ('<html><head/><body>&lt;html&gt;&lt;head/&gt;&lt;body&gt;'
             '&lt;script/&gt;&lt;/body&gt;&lt;/html&gt;</body></html>')
        )


class HTML5FragmentField(TestCase):
    def test_sanitize(self):
        m = HTML5FragmentModel()
        m.html = '<script/>'
        m.clean_fields()
        self.assertEquals(m.html, '&lt;script/&gt;')

    def test_allowed_elements(self):
        m = RestrictedHTML5FragmentModel()
        m.html = '<p><a href="#top">This link</a> takes you to the top</p>'
        m.clean_fields()
        self.assertEquals(m.html, ('&lt;p&gt;<a href="#top">This link</a>'
                                   ' takes you to the top&lt;/p&gt;'))

    def test_allowed_attributes(self):
        m = RestrictedHTML5FragmentModel()
        m.html = ('<span style="width: 300px;" class="myclass">'
                  'Click <a href="www.example.com" target="_top">here</a>'
                  '</span>')
        m.clean_fields()
        self.assertEquals(m.html, ('<span style="width: 300px;">'
                            'Click <a href="www.example.com">here</a></span>'))

    def test_allowed_styles(self):
        m = RestrictedHTML5FragmentModel()
        m.html = ('<span style="width: 300px; height:100px">Blah</span>')
        m.clean_fields()
        self.assertEquals(m.html, '<span style="width: 300px;">Blah</span>')

    def test_self_closing_a_tag(self):
        m = HTML5FragmentModel()
        m.html = '<a name="test"/>'
        m.clean_fields()
        self.assertEquals(m.html, '<a name="test"></a>')

    def test_nbsp(self):
        ''' We store UTF-8, so &nbsp; should be stored as \xc2\xa0 (2 chars)
        '''
        m = HTML5FragmentModel()
        m.html = '<p>&nbsp;</p>&nbsp;'
        m.clean_fields()
        self.assertEquals(m.html, '<p>\xc2\xa0</p>\xc2\xa0')

    def test_charset(self):
        m = HTML5FragmentModel()
        m.html = '<p>Привет</p>'
        m.clean_fields()
        self.assertEquals(m.html, '<p>Привет</p>')


class CKEditorWidgetTest(TestCase):
    def test_default_config(self):
        ck = CKEditor()
        rendered = ck.render("ck", "Test")
        expected = ('<textarea rows="10" cols="40" name="ck">Test</textarea>'
                    '<script type="text/javascript">\n'
                    '<!--\n'
                    'CKEDITOR.basePath = \'/static/js/ckeditor/\';\n'
                    "CKEDITOR.replace('id_ck');\n"
                    '-->\n'
                    '</script>\n')
        self.assertEqual(rendered, expected)

    def test_config_based_on_allowed_tags(self):
        ck = CKEditor(allowed_tags=['a'])
        rendered = ck.render("ck", "Test")
        expected = ('<textarea rows="10" cols="40" name="ck">Test</textarea>'
                    '<script type="text/javascript">\n'
                    '<!--\nCKEDITOR.basePath = \'/static/js/ckeditor/\';'
                    '\nCKEDITOR.replace(\'id_ck\', {"toolbar": [["Link",'
                    ' "Unlink", "Anchor"]]});\n-->\n</script>\n'
                    )
        self.assertEqual(rendered, expected)

    def test_custom_config(self):
        ck = CKEditor(ck_config={'extraPlugins': 'myThing'})
        rendered = ck.render("ck", "Test")
        expected = ('<textarea rows="10" cols="40" name="ck">Test</textarea>'
                    '<script type="text/javascript">\n'
                    '<!--\nCKEDITOR.basePath = \'/static/js/ckeditor/\';\n'
                    'CKEDITOR.replace(\'id_ck\', {"extraPlugins": "myThing"});'
                    '\n-->\n</script>\n')
        self.assertEqual(rendered, expected)


class CustomCKEditor(CKEditor):
    def get_extra_plugins(self):
        plugins = ["myPlugin1", "myPlugin2"]
        return ','.join(plugins)


class CustomCKEditorTest(TestCase):
    def test_config(self):
        ck = CustomCKEditor()
        rendered = ck.render("ck", "Test")
        expected = ('<textarea rows="10" cols="40" name="ck">Test</textarea>'
                    '<script type="text/javascript">\n'
                    '<!--\nCKEDITOR.basePath = \'/static/js/ckeditor/\';\n'
                    "CKEDITOR.replace('id_ck', "
                    '{"extraPlugins": "myPlugin1,myPlugin2"});\n'
                    '-->\n'
                    '</script>\n')
        self.assertEqual(rendered, expected)
