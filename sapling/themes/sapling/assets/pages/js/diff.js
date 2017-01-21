$(document).ready(function() {
    /* I wish we didn't have to do this. We set and unset
     * borders/background colors to allow ins / del images to have the
     * correct ins / del background while also fitting into the
     * .image_frame, which is a fixed width. Currently, image_frame has
     * to be fixed because otherwise the caption will overflow. Maybe
     * there's a way to do this with just CSS, but I couldn't figure it
     * out */
    $('.image_frame_border ins img').each(function() {
        $(this).addClass('force_image_frame_border');
        $(this).parent().parent().parent().addClass('ins');
    });
    $('.image_frame_border del img').each(function() {
        $(this).addClass('force_image_frame_border');
        $(this).parent().parent().parent().addClass('del');
    });
});
