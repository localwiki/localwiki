from urlparse import urljoin
from django.conf import settings
from ckeditor.widgets import CKEditor
import models


class WikiEditor(CKEditor):
    def get_config(self):
        config = super(WikiEditor, self).get_config()
        additional = {
            #'skin': 'sapling',
            'filebrowserInsertimageUploadUrl': '_upload/',
            'filebrowserInsertimageBrowseUrl': '_filebrowser',
            'domcleanupAllowedTags': models.allowed_tags,
            'toolbarCanCollapse': False,
            'enterMode': 1,
            'stylesSet': [{'name': 'Normal', 'element': 'p'},
                          {'name': 'Heading 1', 'element': 'h1'},
                          {'name': 'Heading 2', 'element': 'h2'},
                          {'name': 'Heading 3', 'element': 'h3'},
                          {'name': 'Formatted', 'element': 'pre'}
                        ],
            'indentClasses': ['indent1', 'indent2', 'indent3']
        }
        config.update(additional)
        return config

    def get_plugins(self):
        # We only want the minimal set of plugins
        return ('about,basicstyles,clipboard,colordialog,contextmenu,'
                'elementspath,enterkey,entities,filebrowser,font,format,'
                'horizontalrule,htmldataprocessor,indent,justify,keystrokes,'
                'list,pastetext,removeformat,save,stylescombo,specialchar,tab,'
                'toolbar,undo,wysiwygarea,wsc,sourcearea,selection')

    def get_extra_plugins(self):
        plugins = ['insertimage', 'simpleimage', 'domcleanup', 'seamless',
                   'simpletable', 'simpletabletools', 'customenterkey',
                   'pagelink', 'inheritcss']
        return ','.join(plugins)

    def get_toolbar(self):
        basic_styles = ['Bold', 'Italic', 'Underline', 'Strike']
        styles = ['Styles']
        links = ['PageLink', 'PageAnchor']
        media = ['InsertImage', 'SimpleTable', 'HorizontalRule']
        lists = ['NumberedList', 'BulletedList']
        align = ['JustifyLeft', 'JustifyCenter', 'JustifyRight']
        indent = ['Outdent', 'Indent']
        sub = ['Subscript', 'Superscript']

        toolbar = [basic_styles, styles, links, media, lists, align, indent,
                   sub]
        if settings.DEBUG:
            toolbar = [['Source']] + toolbar
        return toolbar

    class Media:
        js = (
              urljoin(settings.STATIC_URL, 'js/jquery/jquery-1.5.min.js'),
        )
