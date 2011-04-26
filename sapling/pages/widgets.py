from urlparse import urljoin
from django.conf import settings
from ckeditor.widgets import CKEditor
import models


class WikiEditor(CKEditor):
    def get_config(self):
        config = super(WikiEditor, self).get_config()
        additional = {
            'skin': 'sapling',
            'filebrowserInsertimageUploadUrl': '_upload/',
            'domcleanupAllowedTags': models.allowed_tags,
            'contentsCss': urljoin(settings.STATIC_URL,
                                   'css/pages.css'),
            'toolbarCanCollapse': False,
            'enterMode': 1,
        }
        config.update(additional)
        return config

    def get_plugins(self):
        # We only want the minimal set of plugins
        return ('about,basicstyles,clipboard,contextmenu,elementspath,'
                'enterkey,entities,filebrowser,font,format,horizontalrule,'
                'htmldataprocessor,indent,keystrokes,list,'
                'pastetext,removeformat,save,stylescombo,table,'
                'tabletools,specialchar,tab,toolbar,undo,wysiwygarea,wsc,'
                'sourcearea,selection')

    def get_extra_plugins(self):
        plugins = ['insertimage', 'simpleimage', 'domcleanup', 'seamless',
                   'customenterkey', 'pagelink']
        return ','.join(plugins)

    def get_toolbar(self):
        styles = ['Source', 'Bold', 'Italic', 'Underline']
        links = ['PageLink']
        media = ['InsertImage']
        misc = ['Copy', 'Paste', 'Undo', 'Redo']

        return [styles, links, media, misc]

    class Media:
        js = (
              urljoin(settings.STATIC_URL, 'js/jquery/jquery-1.5.min.js'),
        )
