/**
 * seamless plugin. Requires jQuery
 */
(function(){
	var createStyles = function(editor)
	{
	    //make full width
	    var left = jQuery('body').css('margin-left');
	    var right = jQuery('body').css('margin-right');
	    var style = '#cke_' + editor.name + '{ margin-left: -' + left + ';' +
	                                          'margin-right: -' + right + ';' +
	                                          'padding: 0;' +
	                                          'border: 0;' +
	                                          'display: none;' +
	                                        '}';
	    style += '#cke_top_' + editor.name + ' .cke_toolbox { padding-left: ' + left + ' padding-bottom: 3px;}';
	    style += '#cke_' + editor.name + ' span.cke_wrapper { width: 100%; }';
	    // hide editor bottom
	    style += '#cke_bottom_' + editor.name + '{ display: none; }';
	    style += '#cke_contents_' + editor.name + '{ font-size: 0; }';
	    // hide focus outline
	    style += '#cke_' + editor.name + ' .cke_focus { outline: 0 !important;}';
	    // hide scrollbar
	    style += '#cke_contents_' + editor.name + '>iframe{ width: 100%;}';
	    // fixed toolbar
	    style += '.fixedBar { top: 0; position: fixed; width: 100%;' +
	                         'padding-bottom: 0 !important;' +
	                         'border-radius: 0 !important;' +
	                         '-moz-border-radius: 0 !important;' +
	                         '-webkit-border-radius: 0 !important;' +
	                        '}';
	    jQuery('<style type="text/css">' + style + '</style>').appendTo('head');
	};
	var fixToolbar = function(evt)
	{
	    jQuery('#cke_' + evt.editor.name).css('display', 'block');
	    jQuery('span.cke_wrapper').css('padding', '0');
	    var toolBar = jQuery('#cke_top_' + evt.editor.name + ' > div')
	                           .addClass('cke_wrapper');
	    toolBar.wrap(jQuery('<div/>').height(toolBar.parent().height()));
	    var barTop = toolBar.offset().top;
	    jQuery(window).bind('scroll resize', function () {
	       if(jQuery(document).scrollTop() >= barTop)
               toolBar.addClass('fixedBar');
           else
               toolBar.removeClass('fixedBar');
	    });
	}
	var resizeEditor = function( editor )
	{
	    jQuery('#cke_contents_' + editor.name + '>iframe').width(jQuery("#cke_" + editor.name).width());
		if ( !editor.window )
			return;
		var doc = editor.document,
		    currentHeight = editor.window.getViewPaneSize().height, docHeight,
		    docWidth;
		if ( doc.$.body.parentNode )
		{
			var bodyHeight = jQuery(doc.$.body).outerHeight(true);
			var bodyWidth = jQuery(doc.$.body).outerWidth(true);
			var maxBottom = bodyHeight;
			var maxRight = bodyWidth;
			jQuery('span', doc.$).each(function ()
			{
			    var element = jQuery(this);
			    var bottom = element.offset().top + element.outerHeight(true);
			    var right = element.offset().left + element.outerWidth(true);
			    if(bottom > maxBottom)
			       maxBottom = bottom;
			    if(right > maxRight)
			       maxRight = right;
			});
			bodyHeight = maxBottom;
			bodyWidth = maxRight;
			// bodyHeight is inaccurate, plus we want extra room to reduce
			// flickering
			docHeight = bodyHeight + 60;
			docWidth = bodyWidth;
		}
        docHeight = Math.max(docHeight, 200);
		if ( Math.abs(docHeight - currentHeight) > 5)
		{
		    jQuery('#cke_contents_' + editor.name).height(docHeight).contents('>frame').height(docHeight);
		}
		jQuery('#cke_contents_' + editor.name + '>iframe').width(docWidth);
	};
	
	CKEDITOR.plugins.add( 'seamless',
	{
		init : function( editor )
		{
		    createStyles(editor);
		    editor.on('instanceReady', fixToolbar);
			for ( var eventName in { instanceReady:1, contentDom:1, key:1, selectionChange:1, insertElement:1, insertHtml:1 } )
			{
				editor.on( eventName, function( evt )
				{
					setTimeout( function(){ resizeEditor( evt.editor ); }, 100 );
				});
			}
			jQuery(window).resize(function(){resizeEditor(editor);});
		}
	});

})();