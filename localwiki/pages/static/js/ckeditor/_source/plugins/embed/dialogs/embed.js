/*
Sapling pagelink dialog
*/

CKEDITOR.dialog.add( 'embed', function( editor )
{
	var plugin = CKEDITOR.plugins.embed;
	var pagelink_plugin = CKEDITOR.plugins.pagelink;

	return {
		title : 'Embed media',
		minWidth : 300,
		minHeight : 150,
		contents : [
			{
				id : 'info',
				label : gettext('Embed media'),
				title : gettext('Embed media'),
				elements :
				[
					{
						type : 'textarea',
						id : 'code',
						label : gettext('Paste the embed code below:'),
						required: true,
						validate : function()
						{
							var dialog = this.getDialog();
							var func = CKEDITOR.dialog.validate.notEmpty( gettext('Please enter the embed code') );
							return func.apply( this );
						},
						setup : function( data )
						{
							if ( data.code )
								this.setValue( data.code );
						},
						commit : function( data )
						{
							data.code = this.getValue();
						}
					}
				]
			}
		],
		onShow : function()
		{
			var editor = this.getParentEditor(),
				selection = editor.getSelection(),
				element = null,
				data = { code : '' };
			if ( ( element = selection.getStartElement() )
					&& element.is( 'span' ) )
				selection.selectElement( element );
			else
				element = null;
			if( element )
			{
				this._.selectedElement = element;
				data.code = $(element.$).text();
			}
			this.setupContent( data );
		},
		onOk : function()
		{
			var attributes = {},
				data = {},
				me = this,
				editor = this.getParentEditor();

			this.commitContent( data );

			attributes['class'] = 'plugin embed';
			var style = [];
			var node = $(data.code),
				width = node.width(),
				height = node.height();
			if(width)
				style.push('width: ' + width + 'px;');
			if(height)
				style.push('height: ' + height + 'px;');
			if(style.length)
				attributes['style'] = style.join(' ');
			if ( !this._.selectedElement )
			{
				if(jQuery.trim(data.code) == '')
					return;
				// Create element if current selection is collapsed.
				var selection = editor.getSelection(),
					ranges = selection.getRanges( true );

				var text = new CKEDITOR.dom.text( data.code, editor.document );
				ranges[0].insertNode( text );
				ranges[0].selectNodeContents( text );
				selection.selectRanges( ranges );

				// Apply style.
				var style = new CKEDITOR.style( { element : 'span', attributes : attributes } );
				style.apply( editor.document );
				var selected = selection.getStartElement();
				ranges[0].setStartAfter( selected );
				ranges[0].setEndAfter( selected );
				selection.selectRanges( ranges );
			}
			else
			{
				// We're only editing an existing link, so just overwrite the attributes.
				var element = this._.selectedElement;

				element.setAttributes( attributes );
				element.setText( data.code );
			}
		},
		onLoad : function()
		{
		},
		// Inital focus on 'url' field if link is of type URL.
		onFocus : function()
		{
			var pageField = this.getContentElement( 'info', 'code' );
			pageField.select();
		}
	};
});
