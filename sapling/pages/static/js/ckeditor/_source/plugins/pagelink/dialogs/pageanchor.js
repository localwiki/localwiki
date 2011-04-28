/*
Sapling pageanchor dialog
*/

CKEDITOR.dialog.add( 'pageanchor', function( editor )
{
	var plugin = CKEDITOR.plugins.pagelink;

	var processAnchor = function( editor, element )
	{
		var data = {};
		var name = ( element  && (element.data( 'cke-saved-name' ) || element.getAttribute( 'name' ) ) ) || '';
		data.name = name;

		return data;
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
		anchorLang = editor.lang.anchor;

	return {
		title : anchorLang.title,
		minWidth : 250,
		minHeight : 120,
		contents : [
			{
				id : 'info',
				label : anchorLang.info,
				title : anchorLang.info,
				elements :
				[
					{
						type : 'text',
						id : 'name',
						label : 'Anchor name',
						required: true,
						onLoad : function ()
						{
							this.allowOnChange = true;
						},
						onKeyUp : function()
						{
							this.allowOnChange = false;
							this.allowOnChange = true;
						},
						onChange : function()
						{
							if ( this.allowOnChange )		// Dont't call on dialog load.
								this.onKeyUp();
						},
						validate : function()
						{
						},
						setup : function( data )
						{
							this.allowOnChange = false;
							if ( data.name )
								this.setValue( data.name );
							this.allowOnChange = true;

						},
						commit : function( data )
						{
							data.name = this.getValue();
							this.allowOnChange = false;
						}
					}
				]
			}
		],
		onShow : function()
		{
			this.fakeObj = false;
			
			var editor = this.getParentEditor(),
				selection = editor.getSelection(),
				element = null;

			// Fill in all the relevant fields if there's already one anchor selected.
			if ( ( element = selection.getSelectedElement() ) && element.is( 'img' )
					&& element.data( 'cke-real-element-type' )
					&& element.data( 'cke-real-element-type' ) == 'anchor' )
			{
				this.fakeObj = element;
				element = editor.restoreRealElement( this.fakeObj );
				selection.selectElement( this.fakeObj );
			}
			else
				element = null;
			
			this.setupContent( processAnchor.apply( this, [ editor, element ] ) );
		},
		onOk : function()
		{
			var data = {};
			this.commitContent(data);
			// Always create a new anchor, because of IE BUG.
			var name = data.name,
				element = editor.document.createElement( 'a' );
			element.setAttribute('name', name);
			var remove = jQuery.trim(name) == '';
			// Insert a new anchor.
			var fakeElement = editor.createFakeElement( element, 'cke_anchor', 'anchor' );
			if ( !this.fakeObj && !remove)
			{
				// if something is selected, prepend instead of replacing
				ranges = editor.getSelection().getRanges( true );
				if ( ranges.length )
					ranges[0].insertNode( fakeElement );
				else
					editor.insertElement( fakeElement );
			}
			else
			{
				if(remove)
				{
					jQuery(this.fakeObj.$).remove();
					return true;
				}
				fakeElement.replace( this.fakeObj );
				editor.getSelection().selectElement( fakeElement );
			}

			return true;
		},
		onLoad : function()
		{
		},
		// Inital focus on 'url' field if link is of type URL.
		onFocus : function()
		{
			var nameField = this.getContentElement( 'info', 'name' );
			nameField.select();
		}
	};
});