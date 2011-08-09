(function()
{
	function addPluginsButton( editor )
	{
		var menuGroup = 'wikipluginsButton';
		editor.addMenuGroup( menuGroup );
		var uiMenuItems = {
			includePage :
				{
					label : 'Include Page',
					command : 'includepage',
					group : menuGroup,
					className : 'cke_button_includepage',
					onClick: function(){
						// TODO: bring up dialog
					}
				}
		};

		editor.addMenuItems( uiMenuItems );
		editor.ui.add( 'Plugins', CKEDITOR.UI_MENUBUTTON,
			{
				label : 'Insert Object',
				title : 'Insert Object',
				className : 'cke_button_plugins',
				modes : { wysiwyg : 1 },
				onRender: function()
				{
					// TODO: hook up custom plugins?
				},
				onMenu : function()
				{
					return {
						includePage: CKEDITOR.TRISTATE_OFF
					}
					// TODO: turn buttons on/off depending on selection
				}
			});
	}

	CKEDITOR.plugins.add( 'wikiplugins',
	{
		requires : [ 'menubutton' ],

		init : function( editor )
		{
			addPluginsButton( editor );
		}
	});
})();
