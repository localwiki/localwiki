(function()
{
	CKEDITOR.plugins.add( 'includepage',
	{
		requires : [ 'wikiplugins', 'pagelink' ],

		beforeInit : function( editor )
		{
			var config = editor.config;
			if(!config.wikiplugins_menu)
				config.wikiplugins_menu = {};
			config.wikiplugins_menu.includePage =
				{
					label : 'Include Page',
					command : 'includepage',
					icon : this.path + 'images/document-import.png'
				}
			
		},
		
		init : function( editor )
		{
			editor.addCommand( 'includepage', new CKEDITOR.dialogCommand( 'includepage' ) );
			CKEDITOR.dialog.add( 'includepage', this.path + 'dialogs/includepage.js' );
			editor.on( 'doubleclick', function( evt )
			{
				var element = CKEDITOR.plugins.pagelink.getSelectedLink( editor ) || evt.data.element;

				if ( !element.isReadOnly() )
				{
					if ( element.is( 'a' ) )
					{
						if( element.hasClass('plugin') && element.hasClass('includepage') )
							evt.data.dialog =  'includepage';
					}
				}
			});
		}
	});
})();
