/*
Sapling pagelink plugin
*/

CKEDITOR.plugins.add( 'pagelink',
{
	init : function( editor )
	{
		editor.addCommand( 'pagelink', new CKEDITOR.dialogCommand( 'pagelink' ) );
		editor.addCommand( 'pageanchor', new CKEDITOR.dialogCommand( 'pageanchor' ) );
		
		// Add the CSS styles for anchor placeholders.
		var side = editor.lang.dir == 'rtl' ? 'right' : 'left';
		editor.addCss(
			'img.cke_anchor' +
			'{' +
				'background-image: url(' + CKEDITOR.getUrl( this.path + 'images/anchor.gif' ) + ');' +
				'background-position: center center;' +
				'background-repeat: no-repeat;' +
				'border: 1px solid #a9a9a9;' +
				'width: 18px !important;' +
				'height: 18px !important;' +
			'}\n' +
			'a.cke_anchor' +
			'{' +
				'background-image: url(' + CKEDITOR.getUrl( this.path + 'images/anchor.gif' ) + ');' +
				'background-position: ' + side + ' center;' +
				'background-repeat: no-repeat;' +
				'border: 1px solid #a9a9a9;' +
				'padding-' + side + ': 18px;' +
			'}'
		   	);

		editor.ui.addButton( 'PageLink',
			{
				label : editor.lang.link.toolbar,
				command : 'pagelink',
				className : 'cke_button_link'
			} );
		CKEDITOR.dialog.add( 'pagelink', this.path + 'dialogs/pagelink.js' );
		
		editor.ui.addButton( 'PageAnchor',
			{
				label : editor.lang.anchor.toolbar,
				command : 'pageanchor',
				className : 'cke_button_anchor'
			} );
		CKEDITOR.dialog.add( 'pageanchor', this.path + 'dialogs/pageanchor.js' );
		
		editor.on( 'doubleclick', function( evt )
			{
				var element = CKEDITOR.plugins.pagelink.getSelectedLink( editor ) || evt.data.element;

				if ( !element.isReadOnly() )
				{
					if ( element.is( 'a' ) )
					{
						if( element.getAttribute('href'))
							evt.data.dialog =  'pagelink';
					} else if ( element.is('img') && element.data( 'cke-real-element-type' ) == 'anchor' )
					{
						evt.data.dialog = 'pageanchor';
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
					},
					pageanchor :
					{
						label : editor.lang.anchor.menu,
						command : 'pageanchor',
						group : 'link',
						order : 2
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
					
					var isAnchor = ( element.is( 'img' ) && element.data( 'cke-real-element-type' ) == 'pageanchor' );

					if ( !isAnchor )
					{
						if ( !( element = CKEDITOR.plugins.pagelink.getSelectedLink( editor ) ) )
							return null;

						isAnchor = ( element.getAttribute( 'name' ) && !element.getAttribute( 'href' ) );
					}

					return isAnchor ?
							{ pageanchor : CKEDITOR.TRISTATE_OFF } :
							{ pagelink : CKEDITOR.TRISTATE_OFF };
				});
		}
	},
	afterInit : function( editor )
	{
		// Register a filter to displaying placeholders after mode change.

		var dataProcessor = editor.dataProcessor,
			dataFilter = dataProcessor && dataProcessor.dataFilter;

		if ( dataFilter )
		{
			dataFilter.addRules(
				{
					elements :
					{
						a : function( element )
						{
							var attributes = element.attributes;
							if ( attributes.name && !attributes.href )
								return editor.createFakeParserElement( element, 'cke_anchor', 'anchor' );
						}
					}
				});
		}
	},
	requires : [ 'fakeobjects' ]
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
