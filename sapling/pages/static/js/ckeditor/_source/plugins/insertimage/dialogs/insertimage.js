/*
Copyright (c) 2003-2010, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

(function () {
    var insertImageDialog = function (editor, type) {
    	var dialogType = type || 'insertimage';
    	this.uploading = false;
        function sizeImage(img) {
            var maxWidth = 300;
            var maxHeight = 300;
            var oWidth = img.$.width;
            var oHeight = img.$.height;
            if(oWidth === 0)
            {
                // image not loading yet, try again later
                var sizeTimer = setTimeout(function(){sizeImage(img);}, 200);
                img.setCustomData('sizeTimer', sizeTimer);
                return;
            }
            // image loaded enough to resize, clear timer
            var sizeTimer = img.getCustomData('sizeTimer');
            if(sizeTimer)
                clearTimeout(sizeTimer);
            if(oWidth > maxWidth || oHeight > maxHeight)
            {
                var newWidth, newHeight;
                var boxRatio = maxWidth/maxHeight;
                var imgRatio = oWidth/oHeight;
                if(imgRatio > boxRatio)
                {
                    newWidth = maxWidth;
                    newHeight = oHeight * newWidth/oWidth;
                } else {
                    newHeight = maxHeight;
                    newWidth = oWidth * newHeight/oHeight;
                }
                img.setStyle('width', Math.round(newWidth) + 'px');
                img.setStyle('height', Math.round(newHeight) + 'px');
            }
            img.removeAttribute( 'width' );
            img.removeAttribute( 'height' );
            jQuery(window).resize();
        }
        function commitContent() {
            var args = arguments;

            this.foreach(function (widget) {
                if (widget.commit && widget.id) widget.commit.apply(widget, args);
            });
        }
        
        var uploadStarted = function (dialog) {
        	dialog.uploading = true;
        	dialog.disableButton('ok');
        	showSpinner(dialog.getContentElement('Upload', 'imagePicker'));
        }
        
        var uploadFinished = function (dialog, newUrl) {
        	if(dialog.uploading)
        	{
        		refreshFiles(dialog.getContentElement('Upload', 'imagePicker'),
        			function(){ selectImage(newUrl) });
        		dialog.uploading = false;
        		dialog.enableButton('ok');
        	}
        };
        
        var selectImage = function (src) {
        	var selected = false;
        	jQuery('.image_picker a').each(function(){
        		var el = jQuery(this);
        		if(el.attr('href') == src)
        		{
        			selected = el;
        			var container = el.parents('.image_picker').first().parent();
        			container.scrollTop(el.parent().position().top - container.position().top);
        		}
        	});
        	highlight(selected);
        };
        
        var highlight = function (link) {
        	jQuery('.image_picker a').css('font-weight', '').parent().css('background-color','');
        	if(link)
        		link.css('font-weight', 'bold').parent().css('background-color','#ffff99');
        };
        
        var showSpinner = function(picker)
        {
        	var element = picker.getElement().$;
        	var spinner = jQuery('<div class="loading">Uploading your file...</div>');
        	var message = jQuery('.image_picker_msg', element);
            message.empty().append(spinner);
        }
        
        var hideSpinner = function(picker)
        {
        	var element = picker.getElement().$;
        	var message = jQuery('.image_picker_msg', element);
            message.empty();
        }
        
        var refreshFiles = function (picker, callback) {
        	var filekind = dialogType == 'attachfile' ? 'files' : 'images'
        	var element = picker.getElement().$;
            var txtUrl = picker.getDialog().getContentElement('Upload', 'txtUrl');
            var spinner = jQuery('<div class="loading">Loading ' + filekind + '...</div>');
            
            var no_images = jQuery('<em>(No ' + filekind + ' attached to this page)</em>');
            var image_picker = jQuery('.image_picker', element);
            var message = jQuery('.image_picker_msg', element);
            message.empty().append(spinner);
            var browseUrl = filekind == 'images' ? 
                        editor.config.filebrowserInsertimageBrowseUrl :
                        editor.config.filebrowserAttachfileBrowseUrl;
            jQuery.get(browseUrl, function(data){
            	var result = jQuery('ul.file_list', data)
            					.find('a').parent()
            					.click(function(){
            						var link = jQuery(this).find('a').first();
            						var href = link && link.attr('href');
            						if(!href)
            							return;
            						txtUrl.setValue(href);
                                    highlight(link);
                                    return false;
                            	})
                        		.end().end();
                message.empty();
                image_picker.empty();
                if(result.find('a').length)
                	image_picker.append(result);
                else message.append(no_images);
                if(callback)
                	callback();
            });
        };

        var onImgLoadEvent = function () {
            // Image is ready.
            var image = this.imageElement;
            sizeImage(image);
            image.removeListener('load', onImgLoadEvent);
            image.removeListener('error', onImgLoadErrorEvent);
            image.removeListener('abort', onImgLoadErrorEvent);
        };

        var onImgLoadErrorEvent = function () {
            // Error. Image is not loaded.
            var image = this.imageElement;
            var sizeTimer = image.getCustomData('sizeTimer');
            if(sizeTimer)
                clearTimeout(sizeTimer);
            image.removeListener('load', onImgLoadEvent);
            image.removeListener('error', onImgLoadErrorEvent);
            image.removeListener('abort', onImgLoadErrorEvent);
        };

        return {
            title: dialogType == 'attachfile' ? 'Attach File' : 'Insert Image',
            minWidth: 420,
            minHeight: 150,
            onShow: function () {
                this.imageElement = false;

                var editor = this.getParentEditor(),
                    sel = this.getParentEditor().getSelection(),
                    element = sel.getSelectedElement();
                if (element) {
                    this.hide();
                    editor.openDialog('simpleimage');
                }

                this.imageElement = editor.document.createElement('img');
                highlight('');
                this.setupContent();
            },
            onOk: function () {
            	if(this.uploading)
            		return false;
                if(dialogType == 'attachfile') {
                	var linkElement = editor.document.createElement('a');
                	this.commitContent(linkElement);
                	editor.insertElement(linkElement);
                }
                else {
                	this.commitContent(this.imageElement);
                    // Remove empty style attribute.
	                if (!this.imageElement.getAttribute('style')) this.imageElement.removeAttribute('style');
	
	                // Insert a new Image.
	                var spanElement = editor.document.createElement('span');
	                spanElement.setAttribute('class', 'image_frame image_frame_border');
	                sizeImage(this.imageElement);
	                spanElement.append(this.imageElement);
	                editor.insertElement(spanElement);
                }
            },
            onLoad: function () {
                var doc = this._.element.getDocument();
                this.commitContent = commitContent;
            },
            onHide: function () {
                var urlText = this.getContentElement('Upload', 'txtUrl');
                urlText.getElement().hide();

                if (this.imageElement) {
                    this.imageElement.removeListener('load', onImgLoadEvent);
                    this.imageElement.removeListener('error', onImgLoadErrorEvent);
                    this.imageElement.removeListener('abort', onImgLoadErrorEvent);
                }
                delete this.imageElement;
            },
            contents: [{
                id: 'Upload',
                hidden: false,
                filebrowser: 'uploadButton',
                label: 'Choose a file from your computer',
                elements: [{
                    type: 'file',
                    id: 'file',
                    label: 'Choose a file from your computer',
                    style: 'height:40px',
                    size: 34,
                    setup: function () {
                        /* Fix for #327.  Referer header not sent on first
                         * upload.  When dialog is first shown, we load a blank
                         * page from the server in the iframe (same as form
                         * action but using GET method) and reset the form.
                         */
                        if(CKEDITOR.env.gecko) // issue doesn't affect Firefox
                            return;
                        var widget = this;
                        jQuery('#' + this._.frameId).bind('load',
                             function(){
                                 $(this).unbind('load');
                                 widget.reset();
                                 delete widget.setup;
                             }).attr('src', this.action);
                    },
                    onChange: function () {
                        // Patch the upload form before submitting and add the CSRF token and honeypot fields
                        function getCookie(key) {
                            var result;
                            // adapted from the jQuery Cookie plugin
                            return (result = new RegExp('(?:^|; )' + encodeURIComponent(key) + '=([^;]*)').exec(document.cookie)) ? decodeURIComponent(result[1]) : null;
                        }

                        var csrf_cookie = getCookie('csrftoken');
                        if (!csrf_cookie) return;

                        var uploadForm = this.getInputElement().$.form;
                        var csrf = uploadForm.csrfmiddlewaretoken;
                        if (csrf) return;

                        csrf = uploadForm.ownerDocument.createElement('input');
                        csrf.setAttribute('name', 'csrfmiddlewaretoken');
                        csrf.setAttribute('type', 'hidden');
                        csrf.setAttribute('value', csrf_cookie);
                        uploadForm.appendChild(csrf);
                        /* TODO: make this automatic, this is hardcoded to the django-honeypot settings */
                        honeypot = uploadForm.ownerDocument.createElement('input');
                        honeypot.setAttribute('name', 'content2');
                        honeypot.setAttribute('type', 'hidden');
                        uploadForm.appendChild(honeypot);
                        honeypot_js = uploadForm.ownerDocument.createElement('input');
                        honeypot_js.setAttribute('name', 'content2_js');
                        honeypot_js.setAttribute('type', 'hidden');
                        uploadForm.appendChild(honeypot_js);
                        // if there is a file to upload, do that now
                        if (this.getValue()) {
                            this.getDialog().getContentElement('Upload', 'uploadButton').fire('click');
                        	uploadStarted(this.getDialog());
                        }
                    }
                }, {
                    type: 'fileButton',
                    id: 'uploadButton',
                    filebrowser :
                    	{
                    		action : 'QuickUpload',
                    		target : 'Upload:txtUrl',
                    		onSelect : function( fileUrl, errorMessage ) //optional
                    		{
                    			var dialog = this.getDialog();
                    			hideSpinner(dialog.getContentElement('Upload', 'imagePicker'));
                    			if(dialogType == 'insertimage')
                    			{
                    				var imgRegex = /(.png|.jpg|.jpeg|.gif)$/;
                    				if(!imgRegex.test(fileUrl.toLowerCase()))
                    				{
                    					dialog.hide();
                    					editor.openDialog('attachfile');
                    				}
                    			} 
                    		}
                    	},
                    style: 'display:none',
                    label: editor.lang.image.btnUpload,
                    'for': ['Upload', 'file']
                },{
                    type: 'html',
                    id: 'imagePicker',
                    html: 'Select ' + (dialogType == 'attachfile' ? 'a file' : 'an image') + ': <div style="max-height: 8em; overflow-y: auto;"><div class="image_picker_msg"></div><div class="image_picker"></div></div>',
                    style: 'margin-top: 5px',
                    setup: function() {
                        refreshFiles(this);
                    }
                }, {
                    type: 'html',
                    id: 'webImageHint',
                    html: 'or <a href="#">use ' + (dialogType == 'attachfile' ? 'a file' : 'an image') + ' from the web</a>',
                    style: 'float:left;margin-top:5px',
                    onClick: function () {
                        var urlText = this.getDialog().getContentElement('Upload', 'txtUrl');
                        urlText.getElement().show();
                        urlText.focus();
                        return false;
                    }
                }, {
                    type: 'text',
                    id: 'txtUrl',
                    label: dialogType == 'attachfile' ? 'File URL' : 'Image URL',
                    style: 'height: 4em',
                    size: 38,
                    hidden: true,
                    required: true,
                    onChange: function () {
                        var dialog = this.getDialog(),
                            newUrl = this.getValue();

                        //Update original image
                        if (newUrl.length > 0) //Prevent from load before onShow
                        {
                            dialog = this.getDialog();
                            var image = dialog.imageElement;
                            uploadFinished(dialog, newUrl);
                            if(image)
                            {
                              image.on('load', onImgLoadEvent, dialog);
                              image.setAttribute('src', newUrl);
                            }
                        }
                    },
                    commit: function (element) {
                        if (this.getValue() || this.isChanged()) {
                        	if(dialogType == 'attachfile') {
                        		element.setAttribute('href', this.getValue());
                        		element.setText(this.getValue().substring('_files/'.length));
                        	}
                        	else {
	                            element.on('load', onImgLoadEvent, this.getDialog());
	                            element.setAttribute('_cke_saved_src', decodeURI(this.getValue()));
	                            element.setAttribute('src', decodeURI(this.getValue()));
                        	}
                            
                        }
                    },
                    validate: function () {
                        if (this.getValue().length > 0 || this.getDialog().getContentElement('Upload', 'file').getValue().length > 0) return true;
                        alert('No file selected');
                        return false;
                    }
                }]
            }]
        };
    };

    CKEDITOR.dialog.add('insertimage', function (editor) {
        return insertImageDialog(editor);
    });
    
    CKEDITOR.dialog.add('attachfile', function (editor) {
        return insertImageDialog(editor, type='attachfile');
    });
})();
