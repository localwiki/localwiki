/*
Sapling includetag dialog
*/

CKEDITOR.dialog.add( 'includetag', function( editor )
{
	var plugin = CKEDITOR.plugins.includetag;
	var pagelink_plugin = CKEDITOR.plugins.pagelink;

	return {
		title : gettext('List of tagged pages'),
		minWidth : 250,
		minHeight : 120,
		contents : [
			{
				id : 'info',
				label : gettext('List of tagged pages'),
				title : gettext('List of tagged pages'),
				elements :
				[
					{
						type : 'text',
						id : 'tag',
						label : gettext('Tag'),
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
							var func = CKEDITOR.dialog.validate.notEmpty( gettext('Please enter a tag') );
							return func.apply( this );
						},
						setup : function( data )
						{
							this.allowOnChange = false;
							if ( data.tag )
								this.setValue( data.tag );
							this.allowOnChange = true;
						},
						commit : function( data )
						{
							data.tag = this.getValue();
							this.allowOnChange = false;
						}
					},
					{
						type : 'checkbox',
						id : 'showtitle',
						label : gettext('Show title'),
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
								label : gettext('Width'),
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
									[ gettext('pixels'), 'px' ],
									[ gettext('percent'), '%' ]
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
						label : gettext('Align'),
						'default' : '',
						items :
						[
							[ editor.lang.common.alignLeft , 'left'],
							[ gettext('None') , ''],
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
				data = { tag : '', showtitle : true };

			// Fill in all the relevant fields if there's already one link selected.
			if ( ( element = pagelink_plugin.getSelectedLink( editor ) )
					&& element.hasAttribute( 'href' ) )
				selection.selectElement( element );
			else
				element = null;
			if( element )
			{
				this._.selectedElement = element;
				data.tag = decodeURIComponent(element.getAttribute( 'href' ));
				if(data.tag.indexOf('tags/') == 0)
					data.tag = data.tag.substr('tags/'.length);
				if(element.hasClass('includepage_showtitle'))
					data.showtitle = true;
				else data.showtitle = false;
				if(element.hasClass('includepage_left'))
					data.align = 'left';
				if(element.hasClass('includepage_right'))
					data.align = 'right';
				var width = element.getStyle('width');
				if(width)
					data.width = width;
			}
			this.setupContent( data );
			// Set up autocomplete.
			var urlField = this.getContentElement( 'info', 'tag' );
            $('#' + urlField.domId + ' input').autocomplete({source: '/_api/tags/suggest'})
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
			href = encodeURIComponent('tags/' + data.tag);
	
			classes.push('plugin includetag');
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
				if(jQuery.trim(data.tag) == '')
					return;
				// Create element if current selection is collapsed.
				var selection = editor.getSelection(),
					ranges = selection.getRanges( true );

                var fmts = gettext('List of pages tagged "%s"');
				var textLabel = interpolate(fmts, [data.tag]);

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
				element.setHtml( 'List of pages tagged "' + data.tag + '"' );
			}
		},
		onHide : function()
		{
			// Close autocomplete.
			var urlField = this.getContentElement( 'info', 'tag' );
            $('#' + urlField.domId + ' input').autocomplete("destroy");
		},
		// Inital focus on 'url' field if link is of type URL.
		onFocus : function()
		{
			var tagField = this.getContentElement( 'info', 'tag' );
			tagField.select();
		}
	};
});
