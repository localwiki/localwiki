function before_unload(e)
{
    for (var i in CKEDITOR.instances) {
        if(CKEDITOR.instances[i].checkDirty())
        {
	        return e.returnValue = "You've made changes but haven't saved.  Are you sure you want to leave this page?";
        }
    }
}

function reset_dirty() {
    for (var i in CKEDITOR.instances) {
        CKEDITOR.instances[i].resetDirty();
    }
}

function make_editor_simple() {
    CKEDITOR.instances['id_content'].destroy();
    var config = CKEDITOR_config;
    config['toolbar'] = 'simple';
    CKEDITOR.replace('id_content', config);
}

function reset_editor() {
    CKEDITOR.instances['id_content'].destroy();
    var config = CKEDITOR_config;
    config['toolbar'] = 'full';
    CKEDITOR.replace('id_content', CKEDITOR_config);
}

$(document).ready(function() {
    if (window.addEventListener) {
        window.addEventListener('beforeunload', before_unload, false);
    }
    else {
        window.attachEvent('onbeforeunload', beforeUnload);
    }
    $('#content form').submit(reset_dirty);
    $('#editor_actions .cancel').click(reset_dirty);

    enquire.register("screen and (max-width:500px)", {
        match: make_editor_simple,
        unmatch: reset_editor,
    });
    enquire.listen();
});
