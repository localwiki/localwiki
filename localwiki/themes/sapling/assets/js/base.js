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

/* For twitter typeahead */
$(document).ready(function() {
    var remote_url = '/_api/pages/suggest?term=%QUERY';
    if (region_id) {
        remote_url += '&region_id=' + region_id;
    }
    $('#id_q').typeahead([
        {
          name: 'pages',
          remote: remote_url,
        }
    ])
    .on('typeahead:selected', function(e, datum) {
        var url = encodeURIComponent(datum.value.replace(' ', '_'));
        url = url.replace('%2F', '/');
        document.location = '/' + region_slug + '/' + url;
    });
});

/* Add page button */
$(document).ready(function() {
    $('#new_page_button').click(function() {
       $(this).hide()
       $('#new_page_form').show();
       $('#new_page_form #pagename').focus();
    });
});

function getCookie(key) {
    var result;
    // adapted from the jQuery Cookie plugin
    return (result = new RegExp('(?:^|; )' + encodeURIComponent(key) + '=([^;]*)').exec(document.cookie)) ? decodeURIComponent(result[1]) : null;
}

function set_django_tokens(form) {
    // Patch the form -- add the CSRF token and honeypot fields

    var csrf_cookie = getCookie('csrftoken');
    if (!csrf_cookie) return;
    
    csrf = form.ownerDocument.createElement('input');
    csrf.setAttribute('name', 'csrfmiddlewaretoken');
    csrf.setAttribute('type', 'hidden');
    csrf.setAttribute('value', csrf_cookie);
    form.appendChild(csrf);
    
    /* TODO: make this automatic, this is hardcoded to the django-honeypot settings */
    honeypot = form.ownerDocument.createElement('input');
    honeypot.setAttribute('name', 'content2');
    honeypot.setAttribute('type', 'hidden');
    form.appendChild(honeypot);
    honeypot_js = form.ownerDocument.createElement('input');
    honeypot_js.setAttribute('name', 'content2_js');
    honeypot_js.setAttribute('type', 'hidden');
    form.appendChild(honeypot_js);
}
