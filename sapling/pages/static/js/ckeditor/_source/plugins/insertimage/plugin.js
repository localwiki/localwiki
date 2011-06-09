/*
Copyright (c) 2003-2010, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

/**
 * @file WikiImage plugin
 */

CKEDITOR.plugins.add( 'insertimage',
{
	init : function( editor )
	{
		var pluginName = 'insertimage';

		// Register the dialog.
		CKEDITOR.dialog.add( pluginName, this.path + 'dialogs/insertimage.js' );
		CKEDITOR.dialog.add( 'attachfile', this.path + 'dialogs/insertimage.js' );

		// Register the command.
		editor.addCommand( pluginName, new CKEDITOR.dialogCommand( pluginName ) );
		editor.addCommand( 'attachfile', new CKEDITOR.dialogCommand( 'attachfile' ) );

		// Register the toolbar button.
		editor.ui.addButton( 'InsertImage',
			{
				label : editor.lang.common.image,
				command : pluginName,
				className : 'cke_button_image'
			});

		editor.ui.addButton( 'AttachFile',
			{
				label : 'Attach file',
				command : 'attachfile',
				icon : this.path + 'images/paper-clip.png'
			});

		editor.on( 'doubleclick', function( evt )
			{
				var element = evt.data.element;

				if ( element.is( 'img' ) && !element.getAttribute( '_cke_realelement' ) )
					evt.data.dialog = 'simpleimage';
			});
			
		// Highlight button when an image is selected in the editor
		var imgStyle = new CKEDITOR.style( { element : 'img' } );
		editor.attachStyleStateChange( imgStyle, function( state )
      {
        editor.getCommand( pluginName ).setState( state );
      });
	}
} );

