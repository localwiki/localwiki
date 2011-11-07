/*
Sapling pagelink dialog
*/

CKEDITOR.dialog.add( 'includepage', function( editor )
{
	var plugin = CKEDITOR.plugins.includepage;
	var pagelink_plugin = CKEDITOR.plugins.pagelink;

	return {
		title : 'Include Page',
		minWidth : 250,
		minHeight : 120,
		contents : [
			{
				id : 'info',
				label : 'Include Page',
				title : 'Include Page',
				elements :
				[
					{
						type : 'text',
						id : 'page',
						label : 'Page name',
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
							var dialog = this.getDialog();
							var func = CKEDITOR.dialog.validate.notEmpty( 'Please enter a page name' );
							return func.apply( this );
						},
						setup : function( data )
						{
							this.allowOnChange = false;
							if ( data.page )
								this.setValue( data.page );
							this.allowOnChange = true;
						},
						commit : function( data )
						{
							data.page = this.getValue();
							this.allowOnChange = false;
						}
					},
					{
						type : 'checkbox',
						id : 'showtitle',
						label : 'Show page title',
						setup : function( data )
						{
							if ( data.showtitle )
								this.setValue( true );
							else
								this.setValue( false );
						},
						commit : function( data )
						{
							data.showtitle = this.getValue();
						}
					},
					{
						type : 'hbox',
						children :
						[
							{
								type : 'text',
								id : 'width',
								label : 'Width',
								setup : function( data )
								{
									if ( data.width )
										this.setValue( parseInt( data.width, 10 ) );
								},
								commit : function( data )
								{
									if(!this.getValue())
									{
										data.width = '';
										return;
									}
									var value = parseInt( this.getValue(), 10 ),
									unit = this.getDialog().getValueOf( 'info', 'widthType' );
									data.width = '' + value + unit; 
								}
							},
							{
								type : 'select',
								id : 'widthType',
								label : editor.lang.table.widthUnit,
								labelStyle: 'visibility:hidden',
								'default' : 'px',
								items :
								[
									[ 'pixels', 'px' ],
									[ 'percent', '%' ]
								],
								setup : function( data )
								{
									var widthPattern = /^(\d+(?:\.\d+)?)(px|%)$/;
									var widthMatch = widthPattern.exec( data.width );
									if ( widthMatch )
										this.setValue( widthMatch[2] );
								}
							}
						]
					},
					{
						type : 'radio',
						id : 'align',
						label : 'Align',
						'default' : '',
						items :
						[
							[ editor.lang.common.alignLeft , 'left'],
							[ 'None' , ''],
							[ editor.lang.common.alignRight , 'right']
						],
						setup : function( data )
						{
							if ( data.align )
								this.setValue( data.align );
						},
						commit : function( data )
						{
							data.align = this.getValue();
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
				data = { page : '' };

			// Fill in all the relevant fields if there's already one link selected.
			if ( ( element = pagelink_plugin.getSelectedLink( editor ) )
					&& element.hasAttribute( 'href' ) )
				selection.selectElement( element );
			else
				element = null;
			if( element )
			{
				this._.selectedElement = element;
				data.page = decodeURIComponent(element.getAttribute( 'href' ));
				if(element.hasClass('includepage_showtitle'))
					data.showtitle = true;
				if(element.hasClass('includepage_left'))
					data.align = 'left';
				if(element.hasClass('includepage_right'))
					data.align = 'right';
				var width = element.getStyle('width');
				if(width)
					data.width = width;
			}
			this.setupContent( data );
		},
		onOk : function()
		{
			var attributes = {},
				data = {},
				me = this,
				editor = this.getParentEditor(),
				href,
				classes = [];

			this.commitContent( data );
			href = encodeURIComponent(data.page);
	
			classes.push('plugin includepage');
			if(data.showtitle)
				classes.push('includepage_showtitle');
			if(data.align)
				classes.push('includepage_' + data.align);
			attributes['class'] = classes.join(' ');
			attributes[ 'href' ] = attributes[ 'data-cke-saved-href' ] = href;
			if(data.width)
				attributes[ 'style' ] = 'width:' + data.width;
			
			if ( !this._.selectedElement )
			{
				if(jQuery.trim(data.page) == '')
					return;
				// Create element if current selection is collapsed.
				var selection = editor.getSelection(),
					ranges = selection.getRanges( true );

				var textLabel = 'Include page ' + data.page;

				var text = new CKEDITOR.dom.text( textLabel, editor.document );
				ranges[0].insertNode( text );
				ranges[0].selectNodeContents( text );
				selection.selectRanges( ranges );

				// Apply style.
				var style = new CKEDITOR.style( { element : 'a', attributes : attributes } );
				style.type = CKEDITOR.STYLE_INLINE;		// need to override... dunno why.
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
				element.setHtml( 'Include page ' + data.page );
			}
		},
		onLoad : function()
		{
            // Set up autocomplete.
			var urlField = this.getContentElement( 'info', 'page' );
            $('#' + urlField.domId + ' input').autocomplete({source: '/api/pages/suggest'})
		},
		// Inital focus on 'url' field if link is of type URL.
		onFocus : function()
		{
			var pageField = this.getContentElement( 'info', 'page' );
			pageField.select();
		}
	};
});
