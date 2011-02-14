CKEDITOR.plugins.add( 'wikilink',
{
	init : function( editor )
	{
		// Add the link and unlink buttons.
		editor.addCommand( 'wikilink', new CKEDITOR.dialogCommand( 'wikilink' ) );

		editor.ui.addButton( 'wikilink',
			{
				label : editor.lang.link.toolbar,
				command : 'wikilink'
			} );
		
		CKEDITOR.dialog.add( 'wikilink', this.path + 'dialogs/wikilink.js' );
		
	}
} );

CKEDITOR.plugins.wikilink =
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