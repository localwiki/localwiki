/**
 * @file domcleanup plugin
 * 
 * Simplifies and sanitizes inserted (including pasted) HTML.
 */

CKEDITOR.plugins.add( 'domcleanup',
{
    init : function( editor )
    {
        var allowed_tags = ['p','br','a','em','strong','u','img','h1','h2',
        'h3','h4','h5','hr','ul','ol','li','table','thead','tbody','tr','th',
        'td','strike','sub','sup'];
        if(editor.config.domcleanupAllowedTags)
            allowed_tags = editor.config.domcleanupAllowedTags;
        editor.plugins['domcleanup'].allowedTags = allowed_tags;
        editor.plugins['domcleanup'].allowedAttributes = editor.config.domcleanupAllowedAttributes;
        editor.plugins['domcleanup'].allowedStyles = editor.config.domcleanupAllowedStyles;
        
        // Clean up text pasted into 'pre'
		editor.on( 'paste', function( evt )
		{
			var selection = editor.getSelection();
			var element = selection.getStartElement();
			if(element && jQuery(element.$).closest('pre').length)
				editor.plugins['domcleanup'].removeBlocks = true;
		}, null, null, 1);
		
		editor.on( 'paste', function( evt ) {
			editor.plugins['domcleanup'].removeBlocks = false;
		}, null, null, 99999);
    },
    afterInit : function( editor )
    {
        // fix Array.indexOf in IE (we use it later)
        if(!Array.indexOf){
            Array.prototype.indexOf = function(obj){
                for(var i=0; i<this.length; i++){
                    if(this[i]==obj){
                        return i;
                    }
                }
                return -1;
            }
        }
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
                        var custom_tags = editor.plugins['domcleanup'].customAllowedTags;
                        var ok_attributes = editor.plugins['domcleanup'].allowedAttributes;
                        var ok_styles = editor.plugins['domcleanup'].allowedStyles;
                        var block_elements = {
                            'div': 1,
                            'p': 1,
                            'pre': 1,
                            'h1': 1,
                            'h2': 1, 
                            'h3': 1, 
                            'h4': 1, 
                            'h5': 1, 
                            'h6': 1,
                            'hr': 1,
                            'li': 1,
                            'ol': 1,
                            'ul': 1,
                            'dl': 1,
                            'dt': 1,
                            'dd': 1,
                            'table': 1,
                            'tr': 1,
                            'td': 1,
                            'th': 1,
                            'thead': 1,
                            'tbody': 1,
                            'tfoot': 1
                        };
                        if(ok_attributes)
                        {
                        	for(attr in element.attributes)
                            {
                            	if(attr.indexOf('data-cke-') == 0)
                            		continue;
                                if(!ok_attributes[element.name] ||
                                    ok_attributes[element.name]
                                                    .indexOf(attr) < 0){
                                    delete element.attributes[attr];
                                }
                            }
                        }
                        if(ok_styles && element.attributes && element.attributes['style']
                        	&& ok_styles[element.name])
                        {
                        	var css = element.attributes['style'];
                        	var ok_css = [];
                        	var styles = css.split(';'),
                        		i,
                        		style, k, v;

                        	for (i = 0; i < styles.length; i++)
                        	{
                        		style = styles[i].split(':');
                        		k = $.trim(style[0]).toLowerCase(); // IE sometimes has styles in ALL CAPS
                        		v = $.trim(style.slice(1).join(':'));
                        		if (k.length > 0 && v.length > 0
                        			&& ok_styles[element.name].indexOf(k) >= 0)
                        		{
                        			ok_css.push(k + ': ' + v + ';');
                        		}
                        	}
                        	if(!ok_css.length)
                        		delete element.attributes['style'];
                        	else
                        		element.attributes['style'] = ok_css.join(' ');
                        }
                        if(editor.plugins['domcleanup'].removeBlocks)
                        {
                            if(block_elements[element.name])
                            {
                                element.name = '';
                                element.add(new CKEDITOR.htmlParser.element('br'));
                                return element;
                            }
                        }
                        if(ok_tags.indexOf(element.name) > -1)
                        {
                            if(!custom_tags || custom_tags.indexOf(element.name) > -1 )
                                return element;
                        }
                        var remap = {'i': 'em',
                                     'b': 'strong',
                                     'div': 'p'
                                    };
                        if(remap[element.name])
                        {
                            element.name = remap[element.name];
                        }
                        else element.name = '';
                        return element;
                    }
                }
            });
        }
    }
} );

