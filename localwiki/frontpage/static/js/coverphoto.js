$(function() {
    var cover_form = new FormData(document.getElementById('cover_form'));
    var cover_ratio = 3.68421;
    var cover_y_position = 0;
    var cover_x_position = 0;
    var cover_position_axis = 'y';
    var client_w = null;
    var client_h = null;
    var img_w = null;
    var img_h = null;
    // Only show 'change cover' button if they're an admin
    if (region_is_admin) {
        $('#change_cover_button').hover(function () {
            $(this).show();
        });
        $('#cover').hover(
        function () {
            $('#change_cover_button').show();
        },
        function () {
            $('#change_cover_button').hide();
        }
        );
    }

    // Adjust the height of the map cover underlay based on the client's
    // cover width.  We need to do this in JS because of the way the
    // OpenLayers JS works.
    if ($('#cover .underlay.with_map').length > 0) {
        fix_aspect_ratio();
        $(window).resize(function() { fix_aspect_ratio(); });
    }

    $('#change_cover_button').click(function () {
        $('#cover').off('hover');
        uploadCoverPhoto();
    });

    $('#save_cover').click(function () {
        cover_form.append('position_y', cover_y_position);
        cover_form.append('position_x', cover_x_position);
        cover_form.append('client_w', client_w);
        cover_form.append('client_h', client_h);
        cover_form.append('cover_position_axis', cover_position_axis);
        var xhr = new XMLHttpRequest();
        xhr.onload = function () {
            $('.loading').hide();
            alert('Cover photo saved!');
        };
        var spinner = jQuery('<div class="loading"></div>')
        $('#cover').append(spinner);
        xhr.open('POST', document.getElementById('cover_form').action); 
        xhr.send(cover_form);
    });

    function uploadCoverPhoto() {
        // Show cover photo uploader
        // <here>
        // Check for the various File API support.
        if (window.File && window.FileReader && window.FileList && window.Blob) {
            // Great success! All the File APIs are supported.
        } else {
            alert("We don't support changing cover photos on your browser yet. Consider using FireFox or Chrome for cover uploading.");
            return;
        }

        document.getElementById('cover_file').addEventListener('change', handleFileSelect, false);
        $('#cover_file').click();
        $('#change_cover_button').off('hover');
        $('#cover').off('hover');
        $('#change_cover_button').hide();
    }

    function fix_aspect_ratio(img_src) {
        // Set the #cover to the correct aspect ratio.
        var _fix_ratio = function() {
            var client_width = $('#cover').width();
                $('#cover').height(client_width / cover_ratio)
                var client_height = $('#cover').height();
                if (img_w && ((img_w / img_h) > cover_ratio)) {
                    $('#cover .underlay').css('width', 'auto');
                    $('#cover .underlay').css('height', client_height);
                    cover_position_axis = 'x';
                }
                else {
                    cover_position_axis = 'y';
                }
        };

        if (!img_w && img_src) {
            // Get the correct image height/width
            $('body').append('<img src="' + img_src + '" id="calc_image"/>');
            $('#calc_image').load(function() {
                img_w = $('#calc_image').width();
                img_h = $('#calc_image').height();
                $('#calc_image').hide();
                $('body').remove('#calc_image');

                _fix_ratio();
                positionCover(); 
            });
        }
        else {
            _fix_ratio();
        }
    }

    function handleFileSelect(evt) {
        var files = evt.target.files; // FileList object
        var reader = new FileReader();

        // Closure to capture the file information.
        reader.onload = (function(theFile) {
          return function(e) {
            if ($('#cover .underlay.with_map').length > 0) {
                // Doesn't have a photo, so let's replace
                // the map div with an image tag.
                $('#cover .underlay.with_map').replaceWith('<img src="' + e.target.result + '" class="photo underlay"/>')
            }
            else {
                $('#cover img').attr('src', e.target.result);
            }
            client_w = $('#cover').width();
            client_h = $('#cover').height();
            fix_aspect_ratio(e.target.result);
            $(window).resize(function() { fix_aspect_ratio(); });
          };
        })(f);

        // files is a FileList of File objects.
        var f = files[0];  // Just use the first file.
        cover_form.append('file', f);

        // Read in the image file as a data URL.
        reader.readAsDataURL(f);
        
        $('#save_cover').show();
    }

    function positionCover(axis) {
        $('#cover img').css('cursor', 'move');

        $(function() {
            $('#cover img').draggable({
                axis: cover_position_axis,
                containment: 'element',
                stop: function(evt, ui) {
                    client_w = $('#cover').width();
                    client_h = $('#cover').height();
                    cover_y_position = ui.position.top;
                    cover_x_position = ui.position.left;
                }
                });
        });
    }
});


