/*
Copyright (c) 2003-2010, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

/**
 * @file Image plugin
 */

CKEDITOR.plugins.add( 'simpleimage',
{
	init : function( editor )
	{
		var pluginName = 'simpleimage';

		// Register the dialog.
		CKEDITOR.dialog.add( pluginName, this.path + 'dialogs/simpleimage.js' );

		// Register the command.
		editor.addCommand( pluginName, new CKEDITOR.dialogCommand( pluginName ) );

		// Register the toolbar button.
		editor.ui.addButton( 'Image',
			{
				label : editor.lang.common.image,
				command : pluginName
			});

		editor.on( 'doubleclick', function( evt )
			{
				var element = evt.data.element;

				if ( element.is( 'img' ) && !element.getAttribute( '_cke_realelement' ) )
					evt.data.dialog = 'simpleimage';
			});

		// If the "menu" plugin is loaded, register the menu items.
		if ( editor.addMenuItems )
		{
			editor.addMenuItems(
				{
					image :
					{
						label : editor.lang.image.menu,
						command : 'simpleimage',
						group : 'image'
					}
				});
		}

		// If the "contextmenu" plugin is loaded, register the listeners.
		// if ( editor.contextMenu )
		// {
		// 	editor.contextMenu.addListener( function( element, selection )
		// 		{
		// 			if ( !element || !element.is( 'img' ) || element.getAttribute( '_cke_realelement' ) || element.isReadOnly() )
		// 				return null;
		// 
		// 			return { image : CKEDITOR.TRISTATE_OFF };
		// 		});
		// }
	}
} );