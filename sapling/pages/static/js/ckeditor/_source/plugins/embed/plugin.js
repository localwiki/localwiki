(function()
{
	CKEDITOR.plugins.add( 'embed',
	{
		requires : [ 'wikiplugins' ],

		beforeInit : function( editor )
		{
			var config = editor.config;
			if(!config.wikiplugins_menu)
				config.wikiplugins_menu = {};
			config.wikiplugins_menu.embedMedia =
				{
					label : 'Embed media',
					command : 'embed',
					icon : this.path + 'images/edit-code.png'
				}
			
		},
		
		init : function( editor )
		{
			editor.addCommand( 'embed', new CKEDITOR.dialogCommand( 'embed' ) );
			CKEDITOR.dialog.add( 'embed', this.path + 'dialogs/embed.js' );
			editor.on( 'doubleclick', function( evt )
			{
				var element = evt.data.element;
				element = element.getAscendant('span', true);
				if ( element )
				{
					if( element.hasClass('plugin') && element.hasClass('embed') )
						evt.data.dialog =  'embed';
				}
			});
		}
	});
})();
