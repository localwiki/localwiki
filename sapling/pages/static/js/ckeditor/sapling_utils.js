function beforeUnload(e)
{
    for (var i in CKEDITOR.instances) {
        if(CKEDITOR.instances[i].checkDirty())
        {
	        return e.returnValue = "You've made changes but haven't saved.  Are you sure you want to leave this page?";
        }
    }
}

if (window.addEventListener) {
    window.addEventListener('beforeunload', beforeUnload, false);
}
else {
    window.attachEvent('onbeforeunload', beforeUnload);
}
