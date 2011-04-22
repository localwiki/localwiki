/*
Copyright (c) 2003-2010, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

/**
 * @file Image plugin
 */
CKEDITOR.plugins.add( 'simpleimage',
{
	init : function( editor )
	{
		var pluginName = 'simpleimage';

		// Register the dialog.
		CKEDITOR.dialog.add( pluginName, this.path + 'dialogs/simpleimage.js' );

		// Register the command.
		editor.addCommand( pluginName, new CKEDITOR.dialogCommand( pluginName ) );

		// Register the toolbar button.
		editor.ui.addButton( 'Image',
			{
				label : editor.lang.common.image,
				command : pluginName
			});

		editor.on( 'doubleclick', function( evt )
			{
				var element = evt.data.element;

				if ( element.is( 'img' ) && !element.getAttribute( '_cke_realelement' ) )
					evt.data.dialog = 'simpleimage';
			});
		// outerHTML plugin for jQuery
		jQuery.fn.outerHTML = function(s) {
		return (s)
		? this.before(s).remove()
		: jQuery('<p>').append(this.eq(0).clone()).html();
		};
		var showCaption = function (img) {
		    var frame = img.getAscendant('span');
		    if(frame)
		    {
		        if(jQuery(frame.$).find('span.image_caption').length)
		        {
		            caption = jQuery(frame.$).find('span.image_caption');
		            return;
		        }
		        var caption = jQuery('<span class="image_caption editor_temp">Add a caption</span>');
		        caption.click(function(){ jQuery(caption).removeClass('editor_temp'); });
		        jQuery(frame.$).append(caption);
		    }
		}
		
		editor.on('instanceReady', function( evt )
		{
			var editor = evt.editor;
			
		    // click on image -> add placeholder caption
		    editor.document.on('click', function(evt){
		        var element = evt.data.getTarget();
		        if(element.is('img'))
		        {
		          showCaption(element);
		        }
		        else if(!element.is('span'))
		        {
		          jQuery(evt.sender.$).find('.editor_temp').remove();
		        }
		    });
			
		   	jQuery(editor.document.$.body).bind('dragstart', function(evt){
		   		editor.fire('saveSnapshot');
		   		var img = jQuery(evt.target);
	   			if(!img.is('img'))
	   				return;
	   			var oldFrame = img.parent('span.image_frame');
	   			var oldHtml = oldFrame.length ? oldFrame.outerHTML() : img.outerHTML();
	   			img.attr('dragged', '1');
	   			var moveImage = function(evt){
	   				var dropped = jQuery('img[dragged="1"]', editor.document.$);
	   				if(dropped.length)
	   				{
	   					if(dropped[0] != img[0])
	   						oldFrame.remove();
	   					// FF seems to copy frame span also
	   					var frame = dropped.parent('span.image_frame');
	   					if(frame.length)
	   						dropped = frame;
	   					dropped.outerHTML(oldHtml);
	   				}
	   				jQuery(this).unbind('dragend');
	   			};
	   			jQuery(evt.target).bind('dragend', moveImage)
	   					 .parent().bind('dragend', moveImage);
	   		});
		    
		    // delete image -> delete its parent frame
		    editor.document.on( 'keydown', function( evt )
            {
                var keyCode = evt.data.getKeystroke();

                // Backspace OR Delete.
                if ( keyCode in { 8 : 1, 46 : 1 } )
                {
                    var sel = editor.getSelection(),
                        control = sel.getSelectedElement();

                    if ( control && control.is('img'))
                    {
                        control = control.getAscendant('span');
                        if(!control)
                            return;
                        // Make undo snapshot.
                        editor.fire( 'saveSnapshot' );

                        // Delete any element that 'hasLayout' (e.g. hr,table) in IE8 will
                        // break up the selection, safely manage it here. (#4795)
                        var bookmark = sel.getRanges()[ 0 ].createBookmark();
                        // Remove the control manually.
                        control.remove();
                        sel.selectBookmarks( [ bookmark ] );

                        editor.fire( 'saveSnapshot' );

                        evt.data.preventDefault();
                    }
                }
            } );
		});

		// If the "menu" plugin is loaded, register the menu items.
		if ( editor.addMenuItems )
		{
			editor.addMenuItems(
				{
					image :
					{
						label : editor.lang.image.menu,
						command : 'simpleimage',
						group : 'image'
					}
				});
		}

		// If the "contextmenu" plugin is loaded, register the listeners.
		// if ( editor.contextMenu )
		// {
		// 	editor.contextMenu.addListener( function( element, selection )
		// 		{
		// 			if ( !element || !element.is( 'img' ) || element.getAttribute( '_cke_realelement' ) || element.isReadOnly() )
		// 				return null;
		// 
		// 			return { image : CKEDITOR.TRISTATE_OFF };
		// 		});
		// }
	}
} );