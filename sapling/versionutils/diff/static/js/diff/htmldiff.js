$(document).ready(function(){
	alignChanges();
	buildTips();
});

function visualSort(a, b)
{
	var aPos = $(a).position(), bPos = $(b).position();
	if(aPos.top - bPos.top)
		return aPos.top - bPos.top;
	if(aPos.left - bPos.left)
		return aPos.left - bPos.left;
	return 0;
}


function buildTips() {
	var current = 0;
	var toolBar = false, changeText, prev, next;
	var tips = [];
	var setupToolbar = function(){
		if(!toolBar)
		{
			toolBar = $('<div class="diff-toolbar"></div>');
			changeText = $('<span class="diff-toolbar-text"/>').appendTo(toolBar);
			prev = $('<input type="button" value="Previous" />').click(goPrev)
				.appendTo(toolBar);
			next = $('<input type="button" value="Next" />').click(goNext)
				.appendTo(toolBar);
			$('<span class="close-button" title="Close">&times;</span>').click(function(){
				toolBar.animate({ 'margin-top': '-30px'}, function(){ toolBar.hide(); });
			}).css('cursor', 'pointer').appendTo(toolBar);
			toolBar.appendTo(document.body).hide();
		}
		$(changes[current]).data('qtip').show();
		changeText.html((current + 1).toString() + ' of ' + changes.length.toString());
		var tipTop = Math.min($(changes[current]).data('qtip').elements.tooltip.position().top,
							  $(changes[current]).position().top);
		$(document.body).animate({ scrollTop: tipTop - 40 },
							function(){
								if(toolBar.is(':hidden'))
									toolBar.show().animate({ 'margin-top': '0px' });
							});
		prev.attr('disabled', current == 0);
		next.attr('disabled', current == changes.length-1);
	};
	var goNext = function() {
		if(current + 1 <= changes.length - 1)
			current++;
		setupToolbar();
	};
	var goPrev = function() {
		if(current - 1 >= 0)
			current--;
		setupToolbar();
	};
	$('<span class="review-changes">Review changes</span>').click(setupToolbar).appendTo('#title');
	var changes = $("del.diff-html-removed,ins.diff-html-added,span.diff-html-changed")
		.filter(function(){return this.childNodes})
		.sort(visualSort)
		.each(function (index){
			$(this).data('changeIndex', index);
		});
	changes.qtip({
		content: function (api) {
			switch(api.elements.target[0].nodeName)
			{
				case 'DEL': return 'Content was deleted';
				case 'INS': return 'Content was added';
				default : return api.elements.target.first().attr('changes');
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
				var willHide = event.originalEvent.type == 'mousedown'
					|| !toolBar
					|| toolBar.is(':hidden')
					|| changes[current] != api.elements.target[0];
				if(willHide)
					api.elements.target.removeClass('diff-highlight');
				return willHide;
			}
		}
	}).click(function(){
		current = $(this).data('changeIndex');
		setupToolbar();
	});
}


function alignChanges(elem)
{
	var left = $("tr.htmldiff").first().children()[0];
	var right = $("tr.htmldiff").first().children()[1];
	var leftText = [];
	var rightText = [];
	$(left).children().each(function (){
		var texts = $(this).clone().find('del,ins').remove().end().text().split(/\s+/);
		for(var i = 0; i < texts.length; i++)
		{
			if(texts[i].length)
				leftText.push({ text: texts[i], node: this});
		}
	});
	$(right).children().each(function (){
		var texts = $(this).clone().find('del,ins').remove().end().text().split(/\s+/);
		for(var i = 0; i < texts.length; i++)
		{
			if(texts[i].length)
				rightText.push({ text: texts[i], node: this});
		}
	});

	if(leftText.length != rightText.length) // sanity check
		return;

	for(var i = 0; i < leftText.length; i++)
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
	var higher = aPos < bPos ? a : b;
	$(higher).css('margin-top', Math.abs(aPos - bPos));
	$(a).data('aligned', true);
	$(b).data('aligned', true);
}