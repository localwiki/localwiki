/*
Copyright (c) 2003-2010, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.dialog.add( 'wikilink', function( editor )
{
	var plugin = CKEDITOR.plugins.wikilink;

	// Loads the parameters in a selected link to the link dialog fields.
	var emailRegex = /^mailto:([^?]+)(?:\?(.+))?$/,
		urlRegex = /^((?:http|https|ftp|news):\/\/)?(.*)$/;

	var parseLink = function( editor, element )
	{
		var href = ( element  &&  element.getAttribute( 'href' ) ) || '',
			emailMatch,
			urlMatch,
			retval = {};

		if ( ( emailMatch = href.match( emailRegex ) ) )
		{
			retval.type = 'email';
			var email = ( retval.email = {} );
			email.address = emailMatch[ 1 ];
		}
		// urlRegex matches empty strings, so need to check for href as well.
		else if (  href && ( urlMatch = href.match( urlRegex ) ) )
		{
			retval.type = 'url';
			retval.url = {};
			retval.url.protocol = urlMatch[1];
			retval.url.url = urlMatch[2];
		}
		else
			retval.type = 'url';

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
		title : 'Dialog title',
		minWidth : 350,
		minHeight : 230,
		contents : [
			{
				id : 'info',
				label : 'First tab',
				title : 'First tab title',
				elements :
				[	
						{
							type : 'text',
							id : 'url',
							label : 'Page or URL',
							required: true,
							onLoad : function ()
							{
								this.allowOnChange = true;
							},
							onKeyUp : function()
							{
								this.allowOnChange = false;
								// Do stuff as they type
								this.allowOnChange = true;
							},
							onChange : function()
							{
								if ( this.allowOnChange )		// Dont't call on dialog load.
									this.onKeyUp();
							},
							validate : function()
							{
								var func = CKEDITOR.dialog.validate.notEmpty( linkLang.noUrl );
								return func.apply( this );
							},
							setup : function( data )
							{
								this.allowOnChange = false;
								if ( data.url )
									this.setValue( data.url.url );
								this.allowOnChange = true;

							},
							commit : function( data )
							{
								// IE will not trigger the onChange event if the mouse has been used
								// to carry all the operations #4724
								this.onChange();

								if ( !data.url )
									data.url = {};

								data.url.url = this.getValue();
								this.allowOnChange = false;
							}
						},
				]
			}
		],
		onShow : function()
		{
			var editor = this.getParentEditor(),
				selection = editor.getSelection(),
				element = null;

			// Fill in all the relevant fields if there's already one link selected.
			if ( ( element = plugin.getSelectedLink( editor ) ) && element.hasAttribute( 'href' ) )
				selection.selectElement( element );
			else
				element = null;
				
		  console.log(element);

			this.setupContent( parseLink.apply( this, [ editor, element ] ) );
		},
		onOk : function()
		{
		  var editor = this.getParentEditor();
		  console.log('Selection:');
		  console.log(editor.getSelection());
		  console.log('Selected element:');
		  console.log(plugin.getSelectedLink( editor ));
		  var attributes = { href : 'javascript:void(0)/*' + CKEDITOR.tools.getNextNumber() + '*/' },
		      data = { href : attributes.href };
			this.commitContent( data );

			// Compose the URL.
			switch ( data.type || 'url' )
			{
				case 'url':
				  alert('this is a url');
					break;
					
				case 'email':
				  alert('This is an email');
					break;
			}
		},
		onLoad : function()
		{
		},
		onFocus : function()
		{
			urlField = this.getContentElement( 'info', 'url' );
			urlField.select();
		}
	};
});