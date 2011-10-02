/*
Sapling searchbox plugin dialog
*/

CKEDITOR.dialog.add( 'searchbox', function( editor )
{
	var plugin = CKEDITOR.plugins.searchbox;

	return {
		title : 'Search Box',
		minWidth : 250,
		minHeight : 120,
		contents : [
			{
				id : 'info',
				label : 'Search Box',
				title : 'Search Box',
				elements :
				[
					{
						type : 'text',
						id : 'q',
						label : 'Search query',
						required: true,
						setup : function( data )
						{
							if ( data.q )
								this.setValue( data.q );
						},
						commit : function( data )
						{
							data.q = this.getValue();
						}
					}
				]
			}
		],
		onShow : function()
		{
			var editor = this.getParentEditor(),
				selection = editor.getSelection(),
				element = selection.getStartElement(),
				data = { q : '' };

			if ( element.is('input') && element.hasClass('searchbox') )
				selection.selectElement( element );
			else
				element = null;
			if( element )
			{
				this._.selectedElement = element;
				data.q = element.getAttribute( 'value' );
			}
			this.setupContent( data );
		},
		onOk : function()
		{
			var attributes = {},
				data = {},
				me = this,
				editor = this.getParentEditor(),
				value,
				classes = [];

			this.commitContent( data );
			value = data.q;
	
			classes.push('plugin searchbox');
			attributes['class'] = classes.join(' ');
			attributes['type'] = 'text';
			attributes[ 'value' ] =  value;
			
			if ( !this._.selectedElement )
			{
				// Create element if current selection is collapsed.
				var selection = editor.getSelection(),
					ranges = selection.getRanges( true );

				// Apply style.
				var box = new CKEDITOR.dom.element('input');
				box.setAttributes(attributes);
				ranges[0].insertNode(box);
			}
			else
			{
				// We're only editing an existing searchbox, so just overwrite the attributes.
				var element = this._.selectedElement;
				element.setAttributes( attributes );
			}
		},
		onLoad : function()
		{
		},
		// Inital focus on search query field if link is of type URL.
		onFocus : function()
		{
			var qField = this.getContentElement( 'info', 'q' );
			qField.select();
		}
	};
});
