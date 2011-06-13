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
			specialKeys[ 37 ] = this.leftArrow;
			specialKeys[ 8 ] = specialKeys[ 46 ] = this.deleteOrBackspace;
		},
		
		leftArrow : function ( editor )
		{
			var selection = editor.getSelection();
			var element = selection.getStartElement();
			if(element.getName() == 'td')
				return editor.plugins.ckfixes.fixLeftArrowInTable(editor, element, selection);
		},
		
		deleteOrBackspace : function ( editor )
		{
			var selection = editor.getSelection();
			var element = selection.getStartElement();
			if(element.getName() == 'p')
				return editor.plugins.ckfixes.fixDeleteInFirstParagraph(editor, element, selection);
		},
		
		fixLeftArrowInTable : function ( editor, element, selection )
		{
			var address = element.getAddress().slice(1); // ignore <head>, etc
			var max = Math.max.apply(Math, address);
			if(max > 0) // not the first cell
				return;
			var ranges = selection.getRanges();
			if(ranges[0].startOffset > 0) // ignore if not the first char
				return;
			var table = element.getAscendant('table');
			var p = new CKEDITOR.dom.element( 'p' );
			p.appendBogus();
			p.insertBefore(table);
			ranges[0].selectNodeContents(p);
			selection.selectRanges(ranges);
		},
		
		fixDeleteInFirstParagraph : function ( editor, element, selection )
		{
			// don't know how to do this properly yet'
		}
	});
})();
