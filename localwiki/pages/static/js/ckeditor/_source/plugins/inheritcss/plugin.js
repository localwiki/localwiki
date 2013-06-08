/**
 * @file inheritcss plugin
 * Finds all the CSS files included in the page and adds them to CKEditor's
 * contentsCss setting
 */

CKEDITOR.plugins.add( 'inheritcss',
{
    init : function( editor )
    {
        editor.config.contentsCss = new Array();
        jQuery('link[rel="stylesheet"]').each(function (){
            css = jQuery(this).attr('href');
            if(css.indexOf(editor.skinPath) == -1)
                editor.config.contentsCss.push(css);
        });
    }
} );

