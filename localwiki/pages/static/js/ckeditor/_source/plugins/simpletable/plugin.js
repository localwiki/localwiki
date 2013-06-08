/*
Copyright (c) 2003-2011, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.plugins.add( 'simpletable',
{
	init : function( editor )
	{
		var table = CKEDITOR.plugins.table,
			lang = editor.lang.table;

		editor.addCommand( 'simpletable', new CKEDITOR.dialogCommand( 'simpletable' ) );
		editor.addCommand( 'simpleTableProperties', new CKEDITOR.dialogCommand( 'simpleTableProperties' ) );

		editor.ui.addButton( 'SimpleTable',
			{
				label : lang.toolbar,
				command : 'simpletable',
				className : 'cke_button_table'
			});

		CKEDITOR.dialog.add( 'simpletable', this.path + 'dialogs/simpletable.js' );
		CKEDITOR.dialog.add( 'simpleTableProperties', this.path + 'dialogs/simpletable.js' );

		// If the "menu" plugin is loaded, register the menu items.
		if ( editor.addMenuItems )
		{
			editor.addMenuItems(
				{
					table :
					{
						label : lang.menu,
						command : 'simpleTableProperties',
						group : 'table',
						order : 5
					},

					tabledelete :
					{
						label : lang.deleteTable,
						command : 'tableDelete',
						group : 'table',
						order : 1
					}
				} );
		}

		editor.on( 'doubleclick', function( evt )
			{
				var element = evt.data.element;

				if ( element.is( 'table' ) )
					evt.data.dialog = 'simpleTableProperties';
			});

		// If the "contextmenu" plugin is loaded, register the listeners.
		if ( editor.contextMenu )
		{
			editor.contextMenu.addListener( function( element, selection )
				{
					if ( !element || element.isReadOnly() )
						return null;

					var isTable = element.hasAscendant( 'table', 1 );

					if ( isTable )
					{
						return {
							tabledelete : CKEDITOR.TRISTATE_OFF,
							table : CKEDITOR.TRISTATE_OFF
						};
					}

					return null;
				} );
		}
	}
} );
