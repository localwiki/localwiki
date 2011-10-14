(function()
{
	CKEDITOR.plugins.add( 'searchbox',
	{
		requires : [ 'wikiplugins' ],

		beforeInit : function( editor )
		{
			var config = editor.config;
			if(!config.wikiplugins_menu)
				config.wikiplugins_menu = {};
			config.wikiplugins_menu.searchBox =
				{
					label : 'Search Box',
					command : 'searchbox',
					icon : this.path + 'images/magnifier.png'
				}
			
		},
		
		init : function( editor )
		{
			editor.addCommand( 'searchbox', new CKEDITOR.dialogCommand( 'searchbox' ) );
			CKEDITOR.dialog.add( 'searchbox', this.path + 'dialogs/searchbox.js' );
			editor.on( 'doubleclick', function( evt )
			{
				var element = evt.data.element;

				if ( !element.isReadOnly() )
				{
					if ( element.is( 'input' ) )
					{
						if( element.hasClass('plugin') && element.hasClass('searchbox') )
							evt.data.dialog =  'searchbox';
					}
				}
			});
		}
	});
})();
