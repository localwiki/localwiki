/*
* Tagedit - jQuery Plugin
* The Plugin can be used to edit tags from a database the easy way
*
* Examples and documentation at: tagedit.webwork-albrecht.de
*
* Copyright (c) 2010 Oliver Albrecht <info@webwork-albrecht.de>
*
* License:
* This work is licensed under a MIT License
* http://www.opensource.org/licenses/mit-license.php
*
* @author Oliver Albrecht Mial: info@webwork-albrecht.de Twitter: @webworka
* @version 1.2.1 (11/2011)
* Requires: jQuery v1.4+, jQueryUI v1.8+, jQuerry.autoGrowInput
*
* Example of usage:
*
* $( "input.tag" ).tagedit();
*
* Possible options:
*
*  autocompleteURL: '', // url for a autocompletion
*  deleteEmptyItems: true, // Deletes items with empty value
*  additionalListClass: '', // put a classname here if the wrapper ul shoud receive a special class
*  allowEdit: true, // Switch on/off edit entries
*  allowDelete: true, // Switch on/off deletion of entries. Will be ignored if allowEdit = false
*  allowAdd: true, // switch on/off the creation of new entries
*  direction: 'ltr' // Sets the writing direction for Outputs and Inputs
*  animSpeed: 500 // Sets the animation speed for effects
*  autocompleteOptions: {}, // Setting Options for the jquery UI Autocomplete (http://jqueryui.com/demos/autocomplete/)
*  breakKeyCodes: [ 13, 44 ], // Sets the characters to break on to parse the tags (defaults: return, comma)
*  checkNewEntriesCaseSensitive: false, // If there is a new Entry, it is checked against the autocompletion list. This Flag controlls if the check is (in-)casesensitive
*  texts: { // some texts
*      removeLinkTitle: 'Remove from list.',
*      saveEditLinkTitle: 'Save changes.',
*      deleteLinkTitle: 'Delete this tag from database.',
*      deleteConfirmation: 'Are you sure to delete this entry?',
*      deletedElementTitle: 'This Element will be deleted.',
*      breakEditLinkTitle: 'Cancel'
*  }
*/

(function($) {

	$.fn.tagedit = function(options) {
		/**
		* Merge Options with defaults
		*/
		options = $.extend(true, {
			// default options here
			autocompleteURL: null,
			additionalListClass: '',
			allowEdit: true,
			allowDelete: true,
			allowAdd: true,
			direction: 'ltr',
			animSpeed: 200,
			autocompleteOptions: {
				select: function( event, ui ) {
					$(this).val(ui.item.value).trigger('transformToTag', [ui.item.id]);
					return false;
				}
			},
			breakKeyCodes: [ 13, 44 ],
            checkNewEntriesCaseSensitive: false,
			texts: {
				removeLinkTitle: 'Remove from list.',
				saveEditLinkTitle: 'Save changes.',
				deleteLinkTitle: 'Delete this tag from database.',
				deleteConfirmation: 'Are you sure to delete this entry?',
				deletedElementTitle: 'This Element will be deleted.',
				breakEditLinkTitle: 'Cancel'
			}
		}, options || {});

		// no action if there are no elements
		if(this.length == 0) {
			return;
		}

		// set the autocompleteOptions source
		if(options.autocompleteURL) {
			options.autocompleteOptions.source = options.autocompleteURL;
		}

		// Set the direction of the inputs
		var direction= this.attr('dir');
		if(direction && direction.length > 0) {
			options.direction = this.attr('dir');
		}

		var elements = this;

		// init elements
		inputsToList();

		/**
		* Creates the tageditinput from a textinput
		*
		*/
		function inputsToList() {
			elements.each(function() {
				$(this).hide();
				var element_name = $(this).attr('name');
				var html = '<ul class="tagedit-list '+options.additionalListClass+'">';
				var words = $(this).val().split(',');
				$.each(words, function(index, value) {
					var word = $.trim(value);
					if(!word.length)
						return;
					html += '<li class="tagedit-listelement tagedit-listelement-old">';
					html += '<span dir="'+options.direction+'">' + $.trim(value) + '</span>';
					html += '<a class="tagedit-close" title="'+options.texts.removeLinkTitle+'">x</a>';
					html += '</li>';
				});
				html += '<li class="tagedit-listelement tagedit-listelement-new">';
				html += '<input type="text" value="" id="tagedit-input" dir="'+options.direction+'"/>';
				html += '</li>';
				html += '</ul>';
				$(this).after(html);
				$(this).closest('form').submit(function (){
					// before submitting, convert anything in the input into tag
					var input = $(this).find('#tagedit-input');
					if(input.val().length > 0)
						input.trigger('transformToTag');
					return true;
				});
			});
			$('ul.tagedit-list')
				// Set function on the input
				.find('#tagedit-input')
					.each(function() {
						$(this).autoGrowInput({comfortZone: 15, minWidth: 15, maxWidth: 20000});

						// Event ist triggert in case of choosing an item from the autocomplete, or finish the input
						$(this).bind('transformToTag', function(event, id) {
							if(options.allowAdd == true) {
								// Make a new tag in front the input
								html = '<li class="tagedit-listelement tagedit-listelement-old">';
								html += '<span dir="'+options.direction+'">' + $(this).val() + '</span>';
								html += '<a class="tagedit-close" title="'+options.texts.removeLinkTitle+'">x</a>';
								html += '</li>';

								$(this).parent().before(html);
							}
							$(this).val('');

							// close autocomplete
							if(options.autocompleteOptions.source) {
								$(this).autocomplete( "close" );
							}

							updateValue($(this).closest('.tagedit-list')[0]);
						})
						.keydown(function(event) {
							var code = event.keyCode > 0? event.keyCode : event.which;

							switch(code) {
								case 8: // BACKSPACE
									if($(this).val().length == 0) {
										// delete Last Tag
										var list = $(this).closest('.tagedit-list')[0];
										var elementToRemove = $(this).closest('.tagedit-list').find('li.tagedit-listelement-old').last();
										elementToRemove.fadeOut(options.animSpeed, function() {elementToRemove.remove(); updateValue(list);})
										event.preventDefault();
										return false;
									}
									break;
								case 9: // TAB
									var autocomplete_active = $('ul.ui-autocomplete #ui-active-menuitem').length > 0;
									if($(this).val().length > 0  && !autocomplete_active) {
										$(this).trigger('transformToTag');
										event.preventDefault();
										return false;
									} else if (autocomplete_active){
										// let it autocomplete on tab
										return false;
									}
								break;
							}
							return true;
						})
						.keypress(function(event) {
							var code = event.keyCode > 0? event.keyCode : event.which;
							if($.inArray(code, options.breakKeyCodes) > -1) {
								if($(this).val().length > 0 && $('ul.ui-autocomplete #ui-active-menuitem').length == 0) {
									$(this).trigger('transformToTag');
								}
							event.preventDefault();
							return false;
							}
							return true;
						})
						.bind('paste', function(e){
							var that = $(this);
							if (e.type == 'paste'){
								setTimeout(function(){
									that.trigger('transformToTag');
								}, 1);
							}
						})
						.blur(function() {
							if($(this).val().length == 0) {
							}
							else {
								// Delete entry after a timeout
								var input = $(this);
								$(this).data('blurtimer', window.setTimeout(function() {input.val('');}, 500));
							}
						})
						.focus(function() {
							window.clearTimeout($(this).data('blurtimer'));
						});

						if(options.autocompleteOptions.source != false) {
							$(this).autocomplete(options.autocompleteOptions);
						}
					})
				.end()
				.click(function(event) {
					switch(event.target.tagName) {
						case 'A':
							$(event.target).parent().fadeOut(options.animSpeed, function() {
								var list = $(event.target).closest('.tagedit-list')[0];
								$(event.target).parent().remove();
								updateValue(list);
								});
							break;
						case 'INPUT':
						case 'SPAN':
						case 'LI':
							break;
						default:
							$(this).find('#tagedit-input').focus();
					}
					return false;
				})
		};
		function updateValue(tagedit_list)
		{
			var tags = $('li.tagedit-listelement span', tagedit_list).map(function(index, elem){
				return $(elem).text();
			}).get();
			$(tagedit_list).prev().val(tags.join(', '));
		}
	}
})(jQuery);
