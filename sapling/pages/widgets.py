from ckeditor.widgets import CKEditor


class WikiEditor(CKEditor):
    def get_config(self):
        config = super(WikiEditor, self).get_config()
        config.update({'filebrowserInsertimageUploadUrl': 'upload'})
        return config

    def get_plugins(self):
        # We only want the minimal set of plugins
        return ('about,basicstyles,clipboard,contextmenu,elementspath,'
                'enterkey,entities,filebrowser,font,format,horizontalrule,'
                'htmldataprocessor,image,indent,keystrokes,link,list,'
                'pastetext,removeformat,save,showblocks,stylescombo,table,'
                'tabletools,specialchar,tab,toolbar,undo,wysiwygarea,wsc')

    def get_extra_plugins(self):
        plugins = ['insertimage', 'simpleimage']
        return ','.join(plugins)

    def get_toolbar(self):
        styles = ['Bold', 'Italic', 'Underline']
        links = ['Link', 'Unlink']
        media = ['InsertImage']
        misc = ['Copy', 'Paste', 'Undo', 'Redo']

        return [styles, links, media, misc]
