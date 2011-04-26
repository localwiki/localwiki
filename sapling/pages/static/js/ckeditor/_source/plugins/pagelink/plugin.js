/*
Sapling pagelink plugin
*/

CKEDITOR.plugins.add( 'pagelink',
{
	init : function( editor )
	{
		editor.addCommand( 'pagelink', new CKEDITOR.dialogCommand( 'pagelink' ) );

		editor.ui.addButton( 'PageLink',
			{
				label : editor.lang.link.toolbar,
				command : 'pagelink',
				className : 'cke_button_link'
			} );
		CKEDITOR.dialog.add( 'pagelink', this.path + 'dialogs/pagelink.js' );
		
		editor.on( 'doubleclick', function( evt )
			{
				var element = CKEDITOR.plugins.pagelink.getSelectedLink( editor ) || evt.data.element;

				if ( !element.isReadOnly() )
				{
					if ( element.is( 'a' ) && element.getAttribute('href'))
					{
						evt.data.dialog =  'pagelink';
					}
				}
			});

		// If the "menu" plugin is loaded, register the menu items.
		if ( editor.addMenuItems )
		{
			editor.addMenuItems(
				{
					pagelink :
					{
						label : editor.lang.link.menu,
						command : 'pagelink',
						group : 'link',
						order : 1
					}
				});
		}

		// If the "contextmenu" plugin is loaded, register the listeners.
		if ( editor.contextMenu )
		{
			editor.contextMenu.addListener( function( element, selection )
				{
					if ( !element || element.isReadOnly() )
						return null;
						
					if ( !element.is( 'img' ) && element.getAttribute( 'href' ))
					{
						if ( !( element = CKEDITOR.plugins.pagelink.getSelectedLink( editor ) ) )
							return null;
					}

					return  { pagelink : CKEDITOR.TRISTATE_OFF };
				});
		}
	}
} );

CKEDITOR.plugins.pagelink =
{
	/**
	 *  Get the surrounding link element of current selection.
	 * @param editor
	 * @example CKEDITOR.plugins.link.getSelectedLink( editor );
	 * @since 3.2.1
	 * The following selection will all return the link element.
	 *	 <pre>
	 *  <a href="#">li^nk</a>
	 *  <a href="#">[link]</a>
	 *  text[<a href="#">link]</a>
	 *  <a href="#">li[nk</a>]
	 *  [<b><a href="#">li]nk</a></b>]
	 *  [<a href="#"><b>li]nk</b></a>
	 * </pre>
	 */
	getSelectedLink : function( editor )
	{
		try
		{
			var selection = editor.getSelection();
			if ( selection.getType() == CKEDITOR.SELECTION_ELEMENT )
			{
				var selectedElement = selection.getSelectedElement();
				if ( selectedElement.is( 'a' ) )
					return selectedElement;
			}

			var range = selection.getRanges( true )[ 0 ];
			range.shrink( CKEDITOR.SHRINK_TEXT );
			var root = range.getCommonAncestor();
			return root.getAscendant( 'a', true );
		}
		catch( e ) { return null; }
	}
};

CKEDITOR.config.keystrokes.push([CKEDITOR.CTRL + 76 /*L*/, 'pagelink']);
