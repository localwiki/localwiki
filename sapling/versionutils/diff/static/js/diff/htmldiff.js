$(window).load(function(){
	alignChanges();
	addToolTips();
});

function visualSort(a, b)
{
	var aPos = $(a).position(), bPos = $(b).position();
	return aPos.top != bPos.top ? aPos.top - bPos.top : aPos.left - bPos.left;
}

function addToolTips() {
	var current = -1;
	var toolBar = false, changeText, prev, next;
	var showChange = function(index){
		if(current > -1 && current != index)
			$(changes[current]).qtip('api').hide();
		current = index;
		if(!toolBar)
		{
			toolBar = $('<div class="diff-toolbar"></div>');
			changeText = $('<span class="diff-toolbar-text"/>').appendTo(toolBar);
			prev = $('<input type="button" class="little" value="Previous" />').click(goPrev)
				.appendTo(toolBar);
			next = $('<input type="button" class="little" value="Next" />').click(goNext)
				.appendTo(toolBar);
			$('<span class="close-button" title="Close">&times;</span>').click(function(){
				toolBar.animate({ 'margin-top': '-36px'}, function(){ toolBar.hide(); });
			}).css('cursor', 'pointer').appendTo(toolBar);
			toolBar.appendTo(document.body).hide();
		}
		$(changes[current]).data('qtip').show();
		changeText.empty().append('Change ' + (current + 1) + ' of ' + changes.length);
		var tipTop = Math.min($(changes[current]).data('qtip').elements.tooltip.position().top,
							  $(changes[current]).position().top);
		$('html,body').animate({ scrollTop: tipTop - 40 },
							function(){
								if(toolBar.is(':hidden'))
									toolBar.show().animate({ 'margin-top': '0px' });
							});
		prev.attr('disabled', current == 0);
		next.attr('disabled', current == changes.length-1);
	};
	var goNext = function() {
		if(current + 1 <= changes.length - 1)
			showChange(current + 1);
		else showChange(current);
	};
	var goPrev = function() {
		if(current - 1 >= 0)
			showChange(current - 1);
		else showChange(current);
	};
	$('<span class="button">Review changes</span>)')
		.click(function(){
			showChange(0);
		}).insertBefore($('tr.htmldiff').parents('table').first())
		  .wrap('<div class="review-changes">')
		  .parent().append('You can use the &larr; and &rarr; keys, too.');
	var changes = $("del.diff-html-removed,ins.diff-html-added,span.diff-html-changed")
		.sort(visualSort)
		.each(function (index){
			$(this).data('changeIndex', index);
		})
		.qtip({
			content: function (api) {
				switch(api.elements.target[0].nodeName)
				{
					case 'DEL': return 'Content was deleted';
					case 'INS': return 'Content was added';
					default : return decodeURIComponent(
								api.elements.target.first().attr('changes'));
				}
			},
			position: {
				my: 'bottom center',
				at: 'top center'
			},
			hide: 'unfocus mouseleave',
			events: {
				show: function(event, api) {
					if(api.elements.target.is('.diff-html-changed'))
						api.elements.target.addClass('diff-highlight');
				},
				hide: function(event, api) {
					var willHide = !event.originalEvent
						|| event.originalEvent.type == 'mousedown'
						|| !toolBar
						|| toolBar.is(':hidden')
						|| changes[current] != api.elements.target[0];
					if(willHide)
						api.elements.target.removeClass('diff-highlight');
					return willHide;
				}
			}
		})
		.click(function(){
			showChange($(this).data('changeIndex'));
		});

	$(document).keydown(function (evt){
		if(evt.which == 39) // right arrow
			goNext();
		if(evt.which == 37) // left arrow
			goPrev();
	});
}

function getWords(elems)
{
	if(!elems.length)
		elems = [elems];
	var words = [], elem;
	for ( var i = 0; elems[i]; i++ ) {
		elem = elems[i];
		if ( elem.nodeType === 3) {
			words = words.concat(elem.nodeValue.split(/\s+/));
		} else if ( elem.nodeType === 1 && elem.nodeName != 'DEL' && elem.nodeName != 'INS') {
			words = words.concat(getWords(elem.childNodes));
		}
	}
	return words;
}

function wordNodeMap(root)
{
	var map = [];
	$(root).children().each(function (index, elem){
		$.each(getWords(elem), function(index, word){
			word && map.push({ text: word, node: elem});
		});
	});
	return map;
}

function alignChanges(elem)
{
	var left = $("tr.htmldiff").first().children()[0];
	var right = $("tr.htmldiff").first().children()[1];
	var leftText = wordNodeMap(left);
	var rightText = wordNodeMap(right);
	for(var i = 0; i < leftText.length && i < rightText.length; i++)
	{
		var leftNode = leftText[i].node;
		var rightNode = rightText[i].node;
		if($(leftNode).data('aligned') || $(rightNode).data('aligned'))
			continue;
		align(leftNode, rightNode);
	}
}

function align(a, b)
{
	var aPos = $(a).position().top;
	var bPos = $(b).position().top;
	if(aPos != bPos)
	{
		var higher = aPos < bPos ? a : b;
		$(higher).before($('<div/>').height(Math.abs(aPos - bPos)));
	}
	$(a).data('aligned', true);
	$(b).data('aligned', true);
}
