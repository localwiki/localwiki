/*
Copyright (c) 2003-2010, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

(function()
{
	var insertImageDialog = function( editor)
	{
		function commitContent()
		{
			var args = arguments;
			
			this.foreach( function( widget )
			{
				if ( widget.commit &&  widget.id )
					widget.commit.apply( widget, args );
			});
		}
		
		var onImgLoadEvent = function()
		{
			// Image is ready.
			var original = this.originalElement;
			original.setCustomData( 'isReady', 'true' );
			original.removeListener( 'load', onImgLoadEvent );
			original.removeListener( 'error', onImgLoadErrorEvent );
			original.removeListener( 'abort', onImgLoadErrorEvent );
		};

		var onImgLoadErrorEvent = function()
		{
			// Error. Image is not loaded.
			var original = this.originalElement;
			original.removeListener( 'load', onImgLoadEvent );
			original.removeListener( 'error', onImgLoadErrorEvent );
			original.removeListener( 'abort', onImgLoadErrorEvent );
		};

		return {
			title : 'Insert Image',
			minWidth : 420,
			minHeight : 120,
			onShow : function()
			{
				this.imageElement = false;
			
				var editor = this.getParentEditor(),
					sel = this.getParentEditor().getSelection(),
					element = sel.getSelectedElement();
        if(element)
        {
          this.hide();
          editor.openDialog('image');
        }
          
				// Copy of the image
				this.originalElement = editor.document.createElement( 'img' );
				this.originalElement.setAttribute( 'alt', '' );
				this.originalElement.setCustomData( 'isReady', 'false' );

				this.imageElement =  editor.document.createElement( 'img' );
			},
			onOk : function()
			{
			  // if there is a file to upload, do that first
			  if(this.getContentElement('Upload', 'upload').getValue())
			  {
			    this.getContentElement('Upload', 'uploadButton').fire('click');
			    return false;
			  }
        this.imageElement = editor.document.createElement( 'img' );
        this.imageElement.setAttribute( 'alt', '' );

        this.commitContent( this.imageElement );
        
        // Remove empty style attribute.
        if ( !this.imageElement.getAttribute( 'style' ) )
          this.imageElement.removeAttribute( 'style' );

        // Insert a new Image.
        editor.insertElement( this.imageElement );
        this.hide()
			},
			onLoad : function()
			{
				var doc = this._.element.getDocument();
				this.commitContent = commitContent;
			},
			onHide : function()
			{
			  urlText = this.getContentElement('Upload', 'txtUrl');
			  urlText.getElement().hide();
			  
				if ( this.originalElement )
				{
					this.originalElement.removeListener( 'load', onImgLoadEvent );
					this.originalElement.removeListener( 'error', onImgLoadErrorEvent );
					this.originalElement.removeListener( 'abort', onImgLoadErrorEvent );
					this.originalElement.remove();
					this.originalElement = false;		// Dialog is closed.
				}
				delete this.imageElement;
			},
			contents : [
				{
					id : 'Upload',
					hidden : false,
					filebrowser : 'uploadButton',
					label : 'Choose a file from your computer',
					elements :
					[
						{
							type : 'file',
							id : 'upload',
							label : 'Choose a file from your computer',
							style: 'height:40px',
							size : 34,
							validate : function ()
                {
                  if(!this.getValue())
                    return true;
                  // Patch the upload form before submitting and add the CSRF token
                  uploadForm = this.getInputElement().$.form;
                  csrf = uploadForm.csrfmiddlewaretoken;
                  if(csrf)
                    return true;
                  csrf = document.createElement('input');
                  csrf.setAttribute('name', 'csrfmiddlewaretoken');
                  csrf.setAttribute('type', 'hidden');
                  
                  function getCookie(name) {
                      var cookieValue = null;
                      if (document.cookie && document.cookie != '') {
                          var cookies = document.cookie.split(';');
                          for (var i = 0; i < cookies.length; i++) {
                              var cookie = cookies[i];
                              // Does this cookie string begin with the name we want?
                              if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                  break;
                              }
                          }
                      }
                      return cookieValue;
                  }
                  
                  csrf_cookie = getCookie('csrftoken');
                  if(!csrf_cookie)
                    return true;
                  csrf.setAttribute('value', csrf_cookie);
                  uploadForm.appendChild(csrf);
                  return true;
                }
						},
						{
							type : 'fileButton',
							id : 'uploadButton',
							filebrowser : 'Upload:txtUrl',
							style : 'display:none',
							label : editor.lang.image.btnUpload,
							'for' : [ 'Upload', 'upload' ]
						},
						{
						  type : 'html',
						  id : 'webImageHint',
						  html : 'or <span style="color:blue;text-decoration:underline;cursor:pointer;">use an image from the web</span>',
						  style : 'float:left;margin-top:10px',
						  onClick : function()
						          {
						            urlText = this.getDialog().getContentElement('Upload', 'txtUrl');
						            urlText.getElement().show();
						            urlText.focus();
						          }
						},
						{
              type : 'text',
              id : 'txtUrl',
              label : 'Image URL',
              style: 'height:40px',
              size : 38,
              hidden : true,
              required : true,
              onChange : function()
                      {
                        var dialog = this.getDialog(),
                          newUrl = this.getValue();

                        //Update original image
                        if ( newUrl.length > 0 )  //Prevent from load before onShow
                        {
                          dialog = this.getDialog();
                          var original = dialog.originalElement;
                          original.setCustomData( 'isReady', 'false' );
                          original.on( 'load', onImgLoadEvent, dialog );
                          original.setAttribute( 'src', newUrl );
                          if(!this.isVisible())
                          {
                            // must be a file upload
                            dialog.fire('ok');
                          }
                        }
                      },
 
              commit : function( element )
  											{
  												if ( this.getValue() || this.isChanged() )
  												{
  													element.setAttribute( '_cke_saved_src', decodeURI( this.getValue() ) );
  													element.setAttribute( 'src', decodeURI( this.getValue() ) );
  												}
  											},
  						validate : function()
        						    {
            						  if(this.getValue().length > 0 || this.getDialog().getContentElement('Upload', 'upload').getValue().length > 0)
            						    return true;
            						  alert(editor.lang.image.urlMissing );
            						  return false;
            						}
  				  }
  				]
				}
			]
		};
	};

	CKEDITOR.dialog.add( 'insertimage', function( editor )
		{
			return insertImageDialog( editor);
		});
})();
