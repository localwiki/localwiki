from django.conf import settings
from django.utils.translation import ugettext as _

from utils.static import static_url
from utils import reverse_lazy
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
            'domcleanupAllowedAttributes': models.allowed_attributes_map,
            'domcleanupAllowedStyles': models.allowed_styles_map,
            'toolbarCanCollapse': False,
            'disableNativeSpellChecker': False,
            'browserContextMenuOnCtrl': True,
            'enterMode': 1,
            'stylesSet': [{'name': _('Normal'), 'element': 'p'},
                          {'name': _('Heading 1'), 'element': 'h1'},
                          {'name': _('Heading 2'), 'element': 'h2'},
                          {'name': _('Heading 3'), 'element': 'h3'},
                          {'name': _('Formatted'), 'element': 'pre'},
                          {'name': _('Typewriter'), 'element': 'tt'}
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
                   'customsourcearea', 'ckfixes', 'wikiplugins', 'includepage',
                   'includetag', 'embed', 'searchbox']
        return ','.join(plugins)

    def get_toolbar(self):
        basic_styles = ['Bold', 'Italic', 'Underline', 'Strike']
        styles = ['Styles']
        links = ['PageLink', 'PageAnchor']
        media = ['InsertImage', 'AttachFile', 'SimpleTable', 'HorizontalRule',
                 'Plugins']
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
              reverse_lazy('django.views.i18n.javascript_catalog',
                           args=['pages']),
              static_url('js/jquery/jquery-1.7.min.js'),
              static_url('js/jquery/jquery-ui-1.8.16.custom.min.js'),
              static_url('js/ckeditor/sapling_utils.js'),
        )
