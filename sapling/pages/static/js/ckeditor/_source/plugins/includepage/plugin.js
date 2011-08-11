(function()
{
	CKEDITOR.plugins.add( 'includepage',
	{
		requires : [ 'wikiplugins' ],

		beforeInit : function( editor )
		{
			var config = editor.config;
			config.wikiplugins_menu.includePage =
				{
					label : 'Include Page',
					command : 'includepage',
					className : 'cke_button_includepage',
					onClick: function(){
						// TODO: bring up dialog
						alert('hey');
					}
				}
			
		}
	});
})();
