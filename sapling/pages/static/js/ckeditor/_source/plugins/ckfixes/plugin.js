/*
Copyright (c) 2003-2011, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

(function()
{
	CKEDITOR.plugins.add( 'ckfixes',
	{
		init : function( editor )
		{
			var specialKeys = editor.specialKeys;
			specialKeys[ 37 ] = specialKeys[ 38 ] = this.leftOrUpArrow;
			specialKeys[ 8 ] = specialKeys[ 46 ] = this.deleteOrBackspace;
			
			editor.on( 'instanceReady', function( evt )
			{
				jQuery('hr', editor.document.$).live('mousedown', function() {
					var element = CKEDITOR.dom.element.get(this);
					editor.getSelection().selectElement(element);
					return false;
				});
			} );
			editor.on('selectionChange', function( evt ){
				var command = editor.getCommand( 'horizontalrule' ),
					element = evt.data.path.lastElement && evt.data.path.lastElement.getAscendant( 'hr', true );
				jQuery('hr.selected', editor.document.$).removeClass('selected');
				if ( element && element.getName() == 'hr')
				{
					command.setState( CKEDITOR.TRISTATE_ON );
					element.addClass('selected');
				}
				else
					command.setState( CKEDITOR.TRISTATE_OFF );
				
			});
		},
		
		leftOrUpArrow : function ( editor )
		{
			var selection = editor.getSelection();
			var element = selection.getStartElement();
			var table = element.getAscendant('table', true);
			if(table)
				return editor.plugins.ckfixes.fixLeftUpArrowInTable(editor, element, selection);
			var frame = element.getAscendant('span', true);
			if(frame && frame.hasClass('image_frame'))
			{
				return editor.plugins.ckfixes.fixLeftUpArrowInImage(editor, frame, selection);
			}
		},
		
		deleteOrBackspace : function ( editor )
		{
			var selection = editor.getSelection();
			var element = selection.getStartElement();
			if(element && element.getName() == 'hr')
				return editor.plugins.ckfixes.fixDeleteHr(editor, element, selection);
			if(element && element.getName() == 'p')
				return editor.plugins.ckfixes.fixDeleteInFirstParagraph(editor, element, selection);
		},
		
		fixLeftUpArrowInTable : function ( editor, element, selection )
		{
			var address = element.getAddress().slice(1); // ignore <head>, etc
			var max = Math.max.apply(Math, address);
			if(max > 0) // not the first cell
			{
				return;
			}
			var ranges = selection.getRanges();
			if(ranges[0].startOffset > 0) // ignore if not the first char
			{
				return;
			}
			var table = element.getAscendant('table');
			var p = new CKEDITOR.dom.element( 'p' );
			p.appendBogus();
			p.insertBefore(table);
			ranges[0].moveToElementEditablePosition(p);
			selection.selectRanges(ranges);
		},
		
		fixLeftUpArrowInImage : function ( editor, element, selection )
		{
			var ranges = selection.getRanges();
			ranges[0].setStartBefore(element);
			ranges[0].setEndBefore(element);
			selection.selectRanges(ranges);
			return true;
		},
		
		fixDeleteInFirstParagraph : function ( editor, element, selection )
		{
			var address = element.getAddress().slice(1);
			var max = Math.max.apply(Math, address);
			if(max > 0)
			{
				return;
			}
			var contents = element.getHtml();
			if(contents == '' || contents == '<br>')
			{
				var next = element.getNext();
				var ranges = selection.getRanges();
				if(next){
					ranges[0].moveToElementEditablePosition(next);
				}
				selection.selectRanges(ranges);
				element.remove();
				return true;
			}
		},
		
		fixDeleteHr : function (editor, element, selection)
		{
			var ranges = selection.getRanges();
			ranges[0].setStartBefore(element);
			ranges[0].setEndBefore(element);
			selection.selectRanges(ranges);
			element.remove();
			return true;
		}
	});
})();
