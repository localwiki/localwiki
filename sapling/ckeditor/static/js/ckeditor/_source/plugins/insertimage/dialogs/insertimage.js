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
			minHeight : 200,
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
        this.imageElement = editor.document.createElement( 'img' );
				this.imageElement.setAttribute( 'alt', '' );
				this.commitContent( this.imageElement );

				// Remove empty style attribute.
				if ( !this.imageElement.getAttribute( 'style' ) )
					this.imageElement.removeAttribute( 'style' );

				// Insert a new Image.
				editor.insertElement( this.imageElement );
			},
			onLoad : function()
			{
				var doc = this._.element.getDocument();
				this.commitContent = commitContent;
			},
			onHide : function()
			{
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
					label : editor.lang.image.upload,
					elements :
					[
						{
							type : 'file',
							id : 'upload',
							label : editor.lang.image.btnUpload,
							style: 'height:40px',
							size : 38
						},
						{
							type : 'fileButton',
							id : 'uploadButton',
							filebrowser : 'Upload:txtUrl',
							label : editor.lang.image.btnUpload,
							'for' : [ 'Upload', 'upload' ]
						},
						{
              type : 'text',
              id : 'txtUrl',
              label : 'Image URL',
              style: 'height:40px',
              size : 38,
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
                          original.setAttribute( 'src', newUrl );
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
  						validate : CKEDITOR.dialog.validate.notEmpty( editor.lang.image.urlMissing )
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
