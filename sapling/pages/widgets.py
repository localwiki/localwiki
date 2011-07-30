from urlparse import urljoin

from django.conf import settings

from ckeditor.widgets import CKEditor
import models


class WikiEditor(CKEditor):
    def get_config(self):
        config = super(WikiEditor, self).get_config()
        additional = {
            'skin': 'sapling',
            'bodyClass': 'page_editor',
            'filebrowserInsertimageUploadUrl': '_upload',
            'filebrowserInsertimageBrowseUrl': '_filebrowser/images',
            'filebrowserAttachfileUploadUrl': '_upload',
            'filebrowserAttachfileBrowseUrl': '_filebrowser/files',
            'domcleanupAllowedTags': models.allowed_tags,
            'toolbarCanCollapse': False,
            'disableNativeSpellChecker': False,
            'browserContextMenuOnCtrl': True,
            'enterMode': 1,
            'stylesSet': [{'name': 'Normal', 'element': 'p'},
                          {'name': 'Heading 1', 'element': 'h1'},
                          {'name': 'Heading 2', 'element': 'h2'},
                          {'name': 'Heading 3', 'element': 'h3'},
                          {'name': 'Formatted', 'element': 'pre'},
                          {'name': 'Typewriter', 'element': 'tt'}
                        ],
            'indentClasses': ['indent1', 'indent2', 'indent3', 'indent4',
                              'indent5', 'indent6', 'indent7', 'indent8',
                              'indent9', 'indent10'],
            'removeFormatAttributes': '',
            'removeFormatTags': (
                'a,h1,h2,h3,h4,h5,h6,b,big,code,del,dfn,em,'
                'font,i,ins,kbd,q,samp,small,strike,strong,sub,'
                'sup,tt,u,var'),
        }
        config.update(additional)
        return config

    def get_plugins(self):
        # We only want the minimal set of plugins
        return ('about,basicstyles,clipboard,colordialog,contextmenu,'
                'elementspath,enterkey,entities,filebrowser,font,format,'
                'horizontalrule,htmldataprocessor,indent,justify,keystrokes,'
                'list,pastetext,removeformat,save,specialchar,tab,'
                'toolbar,undo,wysiwygarea,wsc,selection')

    def get_extra_plugins(self):
        plugins = ['insertimage', 'simpleimage', 'domcleanup', 'seamless',
                   'simpletable', 'simpletabletools', 'customenterkey',
                   'pagelink', 'inheritcss', 'customstylescombo',
                   'customsourcearea', 'ckfixes']
        return ','.join(plugins)

    def get_toolbar(self):
        basic_styles = ['Bold', 'Italic', 'Underline', 'Strike']
        styles = ['Styles']
        links = ['PageLink', 'PageAnchor']
        media = ['InsertImage', 'AttachFile', 'SimpleTable', 'HorizontalRule']
        lists = ['NumberedList', 'BulletedList']
        align = ['JustifyLeft', 'JustifyCenter', 'JustifyRight']
        indent = ['Outdent', 'Indent']
        sub = ['Subscript', 'Superscript']
        advanced = ['RemoveFormat']

        toolbar = [basic_styles, styles, links, media, lists, align, indent,
                   sub, advanced]
        if settings.DEBUG:
            toolbar.append(['Source'])
        # XXX TODO once everything's working near-perfectly, remove the
        # Source button here:
        else:
            toolbar.append(['Source'])
        return toolbar

    class Media:
        js = (
              urljoin(settings.STATIC_URL, 'js/jquery/jquery-1.5.min.js'),
              urljoin(settings.STATIC_URL, 'js/ckeditor/sapling_utils.js'),
        )
