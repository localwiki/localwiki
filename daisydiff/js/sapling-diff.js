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
	$(elem).addClass("diff-highlight");
	//console.log($(elem).attr("class"));
}

function alignChanges(elem)
{
	var left = $("#diff-table tr").children()[0];
	var right = $("#diff-table tr").children()[1];
	var scanline = 0;
	$(left).find("p").each(function(index){
		align(this, $(right).find("p")[index]);
	});
}

function align(left, right)
{
	var leftPos = $(left).position().top;
	var rightPos = $(right).position().top;
	if(leftPos < rightPos)
	{
		$(left).css('padding-top', rightPos - leftPos);
	} else
	{
		$(right).css('padding-top', leftPos - rightPos);
	}
}