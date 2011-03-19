from ckeditor.widgets import CKEditor
import models


class WikiEditor(CKEditor):
    def get_config(self):
        config = super(WikiEditor, self).get_config()
        additional = {'filebrowserInsertimageUploadUrl': 'upload',
                      'domcleanupAllowedTags': models.allowed_tags,
                      'contentsCss': '',
                     }
        config.update(additional)
        return config

    def get_plugins(self):
        # We only want the minimal set of plugins
        return ('about,basicstyles,clipboard,contextmenu,elementspath,'
                'enterkey,entities,filebrowser,font,format,horizontalrule,'
                'htmldataprocessor,image,indent,keystrokes,link,list,'
                'pastetext,removeformat,save,showblocks,stylescombo,table,'
                'tabletools,specialchar,tab,toolbar,undo,wysiwygarea,wsc,'
                'sourcearea')

    def get_extra_plugins(self):
        plugins = ['insertimage', 'simpleimage', 'domcleanup']
        return ','.join(plugins)

    def get_toolbar(self):
        styles = ['Source', 'Bold', 'Italic', 'Underline']
        links = ['Link', 'Unlink']
        media = ['InsertImage']
        misc = ['Copy', 'Paste', 'Undo', 'Redo']

        return [styles, links, media, misc]
