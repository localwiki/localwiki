/**
 * @file QUnit plugin
 */

CKEDITOR.plugins.add( 'qunit',
{
    init : function( editor )
    {
        CKEDITOR.on('instanceReady', function(ev) {
            runAllTests(ev.editor);
        });
    }
} );

