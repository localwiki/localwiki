(function()
{
	CKEDITOR.plugins.add( 'includetag',
	{
		requires : [ 'wikiplugins', 'pagelink' ],

		beforeInit : function( editor )
		{
			var config = editor.config;
			if(!config.wikiplugins_menu)
				config.wikiplugins_menu = {};
			config.wikiplugins_menu.includeTag =
				{
					label : gettext('List of tagged pages'),
					command : 'includetag',
					icon : this.path + 'images/tag-icon-small.png'
				}
			
		},
		
		init : function( editor )
		{
			editor.addCommand( 'includetag', new CKEDITOR.dialogCommand( 'includetag' ) );
			CKEDITOR.dialog.add( 'includetag', this.path + 'dialogs/includetag.js' );
			editor.on( 'doubleclick', function( evt )
			{
				var element = CKEDITOR.plugins.pagelink.getSelectedLink( editor ) || evt.data.element;

				if ( !element.isReadOnly() )
				{
					if ( element.is( 'a' ) )
					{
						if( element.hasClass('plugin') && element.hasClass('includetag') )
							evt.data.dialog =  'includetag';
					}
				}
			});
		}
	});
})();
