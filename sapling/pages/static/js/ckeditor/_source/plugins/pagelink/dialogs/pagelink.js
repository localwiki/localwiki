/*
Sapling pagelink dialog
*/

CKEDITOR.dialog.add( 'pagelink', function( editor )
{
	var plugin = CKEDITOR.plugins.pagelink;

	// Loads the parameters in a selected link to the link dialog fields.
	var javascriptProtocolRegex = /^javascript:/,
		emailRegex = /^mailto:([^?]+)(?:\?(.+))?$/,
		emailSubjectRegex = /subject=([^;?:@&=$,\/]*)/,
		emailBodyRegex = /body=([^;?:@&=$,\/]*)/,
		anchorRegex = /^#(.*)$/,
		urlRegex = /^(?:http|https|ftp):\/\/(.+)$/,
        userRegex = /^Users\/(.+)/i;
		fileRegex = /^_files\//;

	var parseLink = function(href)
	{
		var javascriptMatch,
			emailMatch,
			anchorMatch,
			urlMatch,
			retval = {};
			
		if ( ( anchorMatch = href.match( anchorRegex ) ) )
		{
			retval.type = 'anchor';
			retval.url = href;
		}
		// Protected email link as encoded string.
		else if ( ( emailMatch = href.match( emailRegex ) ) )
		{
			var subjectMatch = href.match( emailSubjectRegex ),
				bodyMatch = href.match( emailBodyRegex );

			retval.type = 'email';
			var email = ( retval.email = {} );
			email.address = emailMatch[ 1 ];
			subjectMatch && ( email.subject = decodeURIComponent( subjectMatch[ 1 ] ) );
			bodyMatch && ( email.body = decodeURIComponent( bodyMatch[ 1 ] ) );
			retval.url = 'mailto:' + email.address;
		}
		else if ( ( externalMatch = href.match( urlRegex ) ) )
		{
			retval.type = 'external';
			retval.url = href;
		}
		else if ( ( fileMatch = href.match( fileRegex ) ) )
		{
			retval.type = 'file';
			retval.url = href;
		}
		else
		{
			retval.type = 'page';
			retval.url = href;
		}
		
		return retval;
	}
	var processLink = function( editor, element, selected_text )
	{
		var href = ( element  && (element.data( 'cke-saved-href' ) || element.getAttribute( 'href' ) ) ) || '';
        // If there's no link selected, let's default to selected text
        // if it's there.
        if (!href && selected_text)
            href = encodeURIComponent(selected_text);

		var retval = parseLink(href);
		
		// Find out whether we have any anchors in the editor.
		// Get all IMG elements in CK document.
		var elements = editor.document.getElementsByTag( 'img' ),
			realAnchors = new CKEDITOR.dom.nodeList( editor.document.$.anchors ),
			anchors = retval.anchors = [];

		for ( var i = 0; i < elements.count() ; i++ )
		{
			var item = elements.getItem( i );
			if ( item.data( 'cke-realelement' ) && item.data( 'cke-real-element-type' ) == 'anchor' )
				anchors.push( editor.restoreRealElement( item ) );
		}

		for ( i = 0 ; i < realAnchors.count() ; i++ )
			anchors.push( realAnchors.getItem( i ) );

		for ( i = 0 ; i < anchors.length ; i++ )
		{
			item = anchors[ i ];
			anchors[ i ] = { name : item.getAttribute( 'name' ), id : item.getAttribute( 'id' ) };
		}

		// Record down the selected element in the dialog.
		this._.selectedElement = element;

		return retval;
	};

	var setupParams = function( page, data )
	{
		if ( data[page] )
			this.setValue( data[page][this.id] || '' );
	};

	var commitParams = function( page, data )
	{
		if ( !data[page] )
			data[page] = {};

		data[page][this.id] = this.getValue() || '';
	};

	function unescapeSingleQuote( str )
	{
		return str.replace( /\\'/g, '\'' );
	}

	function escapeSingleQuote( str )
	{
		return str.replace( /'/g, '\\$&' );
	}


	var commonLang = editor.lang.common,
		linkLang = editor.lang.link;

	return {
		title : linkLang.title,
		minWidth : 250,
		minHeight : 120,
		contents : [
			{
				id : 'info',
				label : linkLang.info,
				title : linkLang.info,
				elements :
				[
					{
						type : 'text',
						id : 'url',
						label : gettext('Page name or URL'),
						required: true,
						onLoad : function ()
						{
							this.allowOnChange = true;
						},
						onKeyUp : function()
						{
							this.allowOnChange = false;
							// TODO: suggest pages as-you-type

							this.allowOnChange = true;
						},
						onChange : function()
						{
							if ( this.allowOnChange )		// Dont't call on dialog load.
								this.onKeyUp();
						},
						validate : function()
						{
							//var dialog = this.getDialog();

							//var func = CKEDITOR.dialog.validate.notEmpty( linkLang.noUrl );
							//return func.apply( this );
						},
						setup : function( data )
						{
							this.allowOnChange = false;
							if ( data.url )
								this.setValue( data.type == 'page' ? decodeURIComponent(data.url) : data.url);
							this.allowOnChange = true;

						},
						commit : function( data )
						{
							raw = this.getValue();
							parsed = parseLink(raw);
							if(parsed && parsed.type == 'page')
								data.url = encodeURIComponent(raw);
							else data.url = raw;
							this.allowOnChange = false;
						}
					}
				]
			}
		],
		onShow : function()
		{
			var editor = this.getParentEditor(),
				selection = editor.getSelection(),
				element,
				selected_text;
			// Fill in all the relevant fields if there's already a link selected.
			
			if ( ( element = plugin.getSelectedLink( editor ) ) && element.hasAttribute( 'href' ) ) {
				selection.selectElement( element );
            }
            else {
                element = undefined;
            }
            if(!element && selection && selection.getRanges()) {
                // Use selected text to set starting href value, but *only* if
                // the selection is simple text, not images or anything else
                var ranges = selection.getRanges();
                if(ranges.length == 1 &&
                   ranges[0].getCommonAncestor(true, false).type == CKEDITOR.NODE_TEXT)
                {
                    selected_text = String(selection.getNative());
                    if (CKEDITOR.env.ie) {
                        selection.unlock(true);
                        selected_text = String(selection.getNative().createRange().text);
                    }
                }
            }
			this.setupContent( processLink.apply( this, [ editor, element, selected_text ] ) );
			// Set up autocomplete.
			var urlField = this.getContentElement( 'info', 'url' );
            $('#' + urlField.domId + ' input').autocomplete({source: '/_api/pages/suggest'});
		},
		onOk : function()
		{
			var attributes = {},
				removeAttributes = [],
				data = {},
				me = this,
				editor = this.getParentEditor();

			this.commitContent( data );
			data = parseLink(data.url);

			// Compose the URL.
			switch ( data.type || 'page' )
			{
				default:
					var url = data.url || '';
					attributes[ 'data-cke-saved-href' ] = url;
			}
			
			attributes[ 'href' ] = attributes[ 'data-cke-saved-href' ];
			
			if ( !this._.selectedElement )
			{
				if(jQuery.trim(data.url) == '')
					return;
				// Create element if current selection is collapsed.
				var selection = editor.getSelection(),
					ranges = selection.getRanges( true );
				if ( ranges.length == 1 && ranges[0].collapsed )
				{
					var textLabel = attributes[ 'data-cke-saved-href' ];
					if (data.type == 'email') {
						textLabel = data.email.address;
                    }
					else if(data.type == 'page') {
						textLabel = decodeURIComponent(data.url);
                        if (textLabel.match(userRegex)) {
                            // Replace "Users/name" with "name".
                            textLabel = textLabel.match(userRegex)[1];
                        }
                    }

					var text = new CKEDITOR.dom.text( textLabel, editor.document );
					ranges[0].insertNode( text );
					ranges[0].selectNodeContents( text );
					selection.selectRanges( ranges );
				}

				// Apply style.
				var style = new CKEDITOR.style( { element : 'a', attributes : attributes } );
				style.type = CKEDITOR.STYLE_INLINE;		// need to override... dunno why.
				style.apply( editor.document );
				selection = editor.getSelection();
				var selected = selection.getStartElement();
				ranges[0].setStartAfter( selected );
				ranges[0].setEndAfter( selected );
				selection.selectRanges( ranges );
			}
			else
			{
				// We're only editing an existing link, so just overwrite the attributes.
				var element = this._.selectedElement,
					href = element.data( 'cke-saved-href' ) || element.getAttribute('href'),
					textView = element.getHtml();

				element.setAttributes( attributes );
				element.removeAttributes( removeAttributes );
				// Update text view when user changes protocol (#4612).
				if ( href == textView || data.type == 'email' && textView.indexOf( '@' ) != -1 )
				{
					// Short mailto link text view (#5736).
					element.setHtml( data.type == 'email' ?
						data.email.address : attributes[ 'data-cke-saved-href' ] );
				}

				delete this._.selectedElement;
				
				// remove link if there is no url
				if(jQuery.trim(data.url) == '')
					jQuery(element.$).after(jQuery(element.$).html()).remove();
			}
		},
		onHide : function()
		{
			// Close autocomplete.
			var urlField = this.getContentElement( 'info', 'url' );
            $('#' + urlField.domId + ' input').autocomplete("destroy");
		},
		// Inital focus on 'url' field if link is of type URL.
		onFocus : function()
		{
			var urlField = this.getContentElement( 'info', 'url' );
			urlField.select();
		}
	};
});
