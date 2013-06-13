/* Show login/logout in #nav when screen is small. */
function add_login_info_actions() {
    $('#login_info .actions a').each(function() {
        var item = $('<li>');
        item.attr('class', 'remove');
        item.append($(this).clone());
        $('#nav ul').append(item);
    });
};

function hide_login_info_actions() {
    $("#nav ul li.remove").remove()
};

$(function() {
    enquire.register("screen and (max-width:500px)", {
        match: add_login_info_actions,
        unmatch: hide_login_info_actions,
    });
    enquire.listen(); 
});

/* hide-address-bar.js. inlined for speed */
/*! Normalized address bar hiding for iOS & Android (c) @scottjehl MIT License */
(function( win ){
	var doc = win.document;
	
	// If there's a hash, or addEventListener is undefined, stop here
	if( !location.hash && win.addEventListener ){
		
		//scroll to 1
		win.scrollTo( 0, 1 );
		var scrollTop = 1,
			getScrollTop = function(){
				return win.pageYOffset || doc.compatMode === "CSS1Compat" && doc.documentElement.scrollTop || doc.body.scrollTop || 0;
			},
		
			//reset to 0 on bodyready, if needed
			bodycheck = setInterval(function(){
				if( doc.body ){
					clearInterval( bodycheck );
					scrollTop = getScrollTop();
					win.scrollTo( 0, scrollTop === 1 ? 0 : 1 );
				}	
			}, 15 );
		
		win.addEventListener( "load", function(){
			setTimeout(function(){
				//at load, if user hasn't scrolled more than 20 or so...
				if( getScrollTop() < 20 ){
					//reset to hide addr bar at onload
					win.scrollTo( 0, scrollTop === 1 ? 0 : 1 );
				}
			}, 0);
		}, false );
	}
})( this );

/* For our little responsive menu toggler */
$(function() {  
    var pull = $('#pull');  
    menu = $('#nav ul');  
    menuHeight = menu.height();  
  
    $(pull).on('click', function(e) {  
        e.preventDefault();  
        menu.slideToggle(300);
    });  

    $(window).resize(function(){  
        var w = $(window).width();  
        if(w > 320 && menu.is(':hidden')) {  
            menu.removeAttr('style');  
        }  
    });
});
