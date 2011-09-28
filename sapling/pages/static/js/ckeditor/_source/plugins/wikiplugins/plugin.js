/*
 * Menu button for "wiki plugins", which are usually placeholders for some
 * kind of dynamic content, but can really be anything.
 * 
 * To register a wiki plugin, just add its menu item definition to the
 * wikiplugins_menu object in the config.
 */
(function()
{
	function addPluginsButton( editor )
	{
		var menuGroup = 'wikipluginsButton';
		editor.addMenuGroup( menuGroup );
		var menuItems = editor.config.wikiplugins_menu;
		jQuery.each(menuItems, function(itemName, item){
			item.group = menuGroup;
		});

		editor.addMenuItems( menuItems );
		var iconPath = editor.plugins.wikiplugins.path + 'images/puzzle.png';
		editor.ui.add( 'Plugins', CKEDITOR.UI_MENUBUTTON,
			{
				label : 'Insert Object',
				title : 'Insert Object',
				icon :  iconPath,
				modes : { wysiwyg : 1 },
				onRender: function()
				{
					// TODO: hook up custom plugins?
				},
				onMenu : function()
				{
					var states = {};
					jQuery.each(menuItems, function(itemName){
						states[itemName] = CKEDITOR.TRISTATE_OFF;
					});
					return states;
					// TODO: turn buttons on/off depending on selection
				}
			});
	}

	CKEDITOR.plugins.add( 'wikiplugins',
	{
		requires : [ 'menubutton' ],
		beforeInit : function( editor )
		{
		},
		init : function( editor )
		{
			addPluginsButton( editor );
		}
	});
})();
