$(document).ready(function(){
	alignChanges();
	addHandlers();
	
});

function addHandlers()
{
	$("del.diff-html-removed").click(function(){showChanges(this);})
}

function showChanges(elem)
{
}

function alignChanges(elem)
{
	var left = $("#diff-table tr").children()[0];
	var right = $("#diff-table tr").children()[1];
	var leftParagraphs = paragraphs(left);
	var rightParagraphs = paragraphs(right);
	leftParagraphs.each(function(index){
		align(this, rightParagraphs[index]);
	});
}

function paragraphs(scope)
{
	// get paragraphs that exist on both sides
	return $(scope).find("p").filter(function (){
		return $(this).contents().filter(function (){
			if(this.nodeType == 3)
				return $.trim(this.nodeValue) != '';
			var tag = this.tagName.toUpperCase();
			return tag != "DEL" && tag != "INS";
		}).length > 0;
	});
}

function align(a, b)
{
	var aPos = $(a).position().top;
	var bPos = $(b).position().top;
	var higher = aPos < bPos ? a : b;
	$(higher).css('padding-top', Math.abs(aPos - bPos));
}