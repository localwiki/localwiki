/**
 * @file domcleanup plugin
 */

CKEDITOR.plugins.add( 'domcleanup',
{
    init : function( editor )
    {
        var allowed_tags = ['p','a','em','strong','u','img','h1','h2','h3',
        'h4','h5','hr','ul','ol','li','table','thead','tbody','tr','th','td'];
        if(editor.config.domcleanupAllowedTags)
            allowed_tags = editor.config.domcleanupAllowedTags;
        editor.plugins['domcleanup'].allowedTags = allowed_tags;

        editor.on( 'paste', function( evt )
        {
            console.log(evt.data.html);
        });
        
    },
    afterInit : function( editor )
    {
        var dataProcessor = editor.dataProcessor,
        dataFilter = dataProcessor && dataProcessor.dataFilter;
        if ( dataFilter )
        {
            dataFilter.addRules(
            {
                elements :
                {
                    $ : function (element)
                    {
                        element.name = element.name.toLowerCase();
                        var drop_tags = ['style','script','head'];
                        if(drop_tags.indexOf(element.name) != -1)
                            return false;
                        var ok_tags = editor.plugins['domcleanup'].allowedTags;
                        var ok_attributes = {
                            'a' : ['name','href','_cke_saved_href'],
                            'img' : ['src','_cke_saved_src','alt','width',
                                     'height','style'],
                             'table' : ['width'],
                            'th': ['colspan', 'rowspan'],
                            'td': ['colspan', 'rowspan'],
                        };
                        for(attr in element.attributes)
                        {
                            if(!ok_attributes[element.name] ||
                                ok_attributes[element.name]
                                                .indexOf(attr) < 0)
                                delete element.attributes[attr];
                        }
                        if(ok_tags.indexOf(element.name) > -1)
                            return element;
                        var remap = {'br':'p',
                                     'i': 'em',
                                     'b': 'strong',
                                    };
                        if(remap[element.name])
                        {
                            element.name = remap[element.name];
                            if(element.isEmpty &&
                              !(element.children && element.children.length) &&
                              element.parent && element.parent.name == 'p' &&
                              element.parent.children.length == 1)
                                element.name = '';
                        }
                        else element.name = '';
                        return element;
                    }
                }
            });
        }
    }
} );

