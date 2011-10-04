SaplingMap = {

    is_dirty: false,

    init_openlayers: function() {
        OpenLayers.Control.LayerSwitcher.prototype.roundedCorner = false;
        var base_initOptions = olwidget.Map.prototype.initOptions;
        /* Resize map to fit content area */
        olwidget.Map.prototype.initOptions = function(options) {
            var opts = base_initOptions.call(this, options) 
            var border_height = 0;
            var map_height = $(window).height() - $('#header').outerHeight() - $('#main_header').outerHeight() - $('#content_header').outerHeight() - $('#content_footer').outerHeight() - ($('#content_wrapper').outerHeight() - $('#content').outerHeight() - border_height);
            opts['mapDivStyle']['height'] = map_height + 'px';
            opts['mapDivStyle']['width'] = '100%';
            // Remove the dummy CSS border we put in to get the map
            // height immediately.
            $('#content_wrapper').css('border', 'none');
            return opts;

        }
        olwidget.EditableLayerSwitcher.prototype.roundedCorner = false;
        var base_onClick = olwidget.EditingToolbar.prototype.onClick;
        olwidget.EditingToolbar.prototype.onClick = function (ctrl, evt) {
            if (ctrl.active) {
                // If the control is already active and it's clicked on
                // then we want to deactivate it.
                base_onClick.call(this, ctrl, evt);
                ctrl.deactivate();
                var layer = SaplingMap._get_editing_layer(map);
                SaplingMap._set_modify_control(layer);
            }
            else {
                base_onClick.call(this, ctrl, evt);
            }
        }
    },

    setup_map: function(map) {
        if (window.addEventListener) {
            window.addEventListener('beforeunload', this.beforeUnload, false);
        }
        else {
            window.attachEvent('onbeforeunload', this.beforeUnload);
        } 
        $('#content form').submit(function() { SaplingMap.is_dirty = false; });
        $('#editor_actions .cancel').click(function() { SaplingMap.is_dirty = false; });

        if(map.opts.dynamic) {
            this.setup_dynamic_map(map);
        }
        this._open_editing(map);
    },

    setup_dynamic_map: function(map) {
        var layer = map.vectorLayers[0];
        layer.dataExtent = map.getExtent();
        loadObjects = this._loadObjects;
        displayRelated = this._displayRelated;
        // make popups persistent when zooming
        map.events.remove('zoomend');
        layer.events.register("moveend", null, function(evt) {
          if(evt.zoomChanged
             || !layer.dataExtent
             || !layer.dataExtent.containsBounds(map.getExtent())) {
             loadObjects(map, layer, function(){ displayRelated(map); });
          }
          else {
              displayRelated(map);
          }
        });
        layer.events.register("featureselected", null, function(evt) {
          var feature = evt.feature;
          var featureBounds = feature.geometry.bounds;
          $('#results_pane').css('display', 'block');
          $('.mapwidget').css('float', 'left');
          size_map();
          map.updateSize();
          if(feature.geometry.CLASS_NAME != "OpenLayers.Geometry.Point")
          {
              map.zoomToExtent(featureBounds);
          }
          $('#header_title_detail').empty().append(' for ' + feature.attributes.html);
          var zoomedStyle = $.extend({}, 
              layer.styleMap.styles.select.defaultStyle,
              { fillOpacity: '0', strokeDashstyle: 'dash' });
          if(feature.geometry.CLASS_NAME != "OpenLayers.Geometry.Point")
          {
              feature.style = zoomedStyle;
              layer.drawFeature(feature);
          }
          displayRelated(map);
        });
        layer.events.register("featureunselected", null, function(evt) {
          evt.feature.style = evt.feature.defaultStyle;
          layer.drawFeature(evt.feature);
        })
        loadObjects(map, layer);
    },

    beforeUnload: function(e) {
        if(SaplingMap.is_dirty) {
            return e.returnValue = "You've made changes but haven't saved.  Are you sure you want to leave this page?";
        }
    },

    _displayRelated: function(map) {
        var layer = map.vectorLayers[0];
        var highlightResult = function (result, feature) {
            var lonlat = feature.geometry.getBounds().getCenterLonLat();
            var infomap = map;
            var popup = new olwidget.Popup(null,
                lonlat, null, feature.attributes.html, null, false,
                null,
                map.opts.popupDirection,
                map.opts.popupPaginationSeparator);
            popup.panMapIfOutOfView = false;
            var existingPopup = map.popups.length && map.popups[0];
            if(existingPopup)
                map.removePopup(existingPopup);
            map.addPopup(popup);
            feature.style = layer.styleMap.styles.select.defaultStyle;
            layer.drawFeature(feature);
            $(result).bind('mouseout', function(){
                $(this).unbind('mouseout');
                map.removePopup(popup);
                feature.style = feature.defaultStyle;
                layer.drawFeature(feature);
                if(existingPopup)
                    map.addPopup(existingPopup);
            });
        };
        var setAlpha = function(feature, viewedArea) {
            if(feature.geometry.CLASS_NAME == "OpenLayers.Geometry.Polygon")
            {
                var alpha =  0.5 - 0.5 * Math.min(1, feature.geometry.getArea()/viewedArea);
                var polyStyle = $.extend({}, 
                          feature.layer.styleMap.styles['default'].defaultStyle,
                          { fillOpacity: alpha });
                feature.style = polyStyle;
                feature.defaultStyle = polyStyle;
                feature.layer.drawFeature(feature);
            }
        };
        var selectedFeature = layer.selectedFeatures && layer.selectedFeatures[0];
        var header = 'Things on this map:';
        var results = $('<ol>');
        var viewedArea = map.getExtent().toGeometry().getArea();
        $.each(layer.features, function(index, feature) {
           if(feature == selectedFeature)
                return;
           setAlpha(feature, viewedArea);
           var listResult = false;
           if(selectedFeature)
           {
               if(selectedFeature.geometry.CLASS_NAME == "OpenLayers.Geometry.Polygon")
               {
                   header = 'Things inside ' + selectedFeature.attributes.html + ':';
                   $.each(feature.geometry.getVertices(), function(ind, vertex){
                       if(selectedFeature.geometry.containsPoint(vertex))
                       {
                           listResult = true;
                           return false;
                       }
                   });
               } else {
                   var threshold = 500; // TODO: what units is this?
                   header = 'Things near ' + selectedFeature.attributes.html + ':';
                   listResult = selectedFeature.geometry.distanceTo(feature.geometry) < threshold;
                   if(feature.geometry.containsPoint)
                       listResult = listResult && !feature.geometry.containsPoint(selectedFeature.geometry);
               }
           }
           if(listResult || !selectedFeature)
           {
               var result = $('<li class="map_result">')
                            .html(feature.attributes.html)
                            .bind('mouseover', function (){
                                highlightResult(this, feature);
                            })
                            .bind('click', function (evt){
                                // hack to prevent olwidget from placing popup incorrectly
                                var mapSize = map.getSize();
                                var center = { x: mapSize.w / 2, y: mapSize.h / 2};
                                map.selectControl.handlers.feature.evt.xy = center;
                                map.selectControl.unselectAll();
                                map.selectControl.select(feature);
                            });
               results.append(result);
           }
        });
        $('#results_pane').empty().append($('<h3/>').html(header)).append(results);
    },

    _loadObjects: function(map, layer, callback) {
        var selectedFeature = layer.selectedFeatures && layer.selectedFeatures[0];
        var setAlpha = this._setAlpha;
        var extent = map.getExtent().scale(1.5);
        var bbox = extent.clone().transform(layer.projection,
                       new OpenLayers.Projection('EPSG:4326')).toBBOX();
              
        var zoom = map.getZoom();
        var myDataToken = Math.random();
        layer.dataToken = myDataToken;
        $.get('_objects/', { 'bbox': bbox, 'zoom': zoom }, function(data){
            if(layer.dataToken != myDataToken)
            {
                return;
            }
            layer.dataExtent = extent;
            var temp = new olwidget.InfoLayer(data);
            temp.visibility = false;
            map.addLayer(temp);
            layer.removeAllFeatures();
            if(selectedFeature)
            {
              layer.addFeatures(selectedFeature);
              layer.selectedFeatures = [selectedFeature];
            }
            $.each(temp.features, function(index, feature) {
              feature.map = map;
              if(selectedFeature && selectedFeature.geometry.toString() == feature.geometry.toString())
                  return;
              layer.addFeatures(feature);
            });
            map.removeLayer(temp);
            if(callback){
                callback();
            }
        })
    },

    _registerEvents: function(map, layer) {
        // Switch to "modify" mode after adding a feature.
        var self = this;
        layer.events.register("featureadded", null, function () {
            self.is_dirty = true;
            self._set_modify_control(layer);
        });

        layer.events.register("featuremodified", null, function () {
            self.is_dirty = true;
        });

        // Key commands for undo/redo.
        var undo_button = this._get_undo_button(layer.controls);
        var redo_button = this._get_redo_button(layer.controls);
        var KeyboardDefaults = OpenLayers.Class(OpenLayers.Control.KeyboardDefaults, {
            defaultKeyPress: function(evt) {
                if (evt.ctrlKey) {
                    switch(evt.keyCode) {
                        case 90:
                            // Shift-Control-Z is redo
                            if (evt.shiftKey) {
                                redo_button.trigger();
                            }
                            // Control-Z
                            else {
                                undo_button.trigger();
                            }
                            break;
                        case 89: // Control-Y is also redo
                            redo_button.trigger();
                            break;
                    }
                }
                return OpenLayers.Control.KeyboardDefaults.prototype.defaultKeyPress.call(this, evt);
            },
        });
        map.addControl(new KeyboardDefaults());
    },

    _get_undo_button: function(controls) {
        for (var i = 0; i < controls.length; i++) {
            if (controls[i].title == 'Undo') {
                return controls[i];
            }
        }
    },

    _get_redo_button: function(controls) {
        for (var i = 0; i < controls.length; i++) {
            if (controls[i].title == 'Redo') {
                return controls[i];
            }
        }
    },

    _set_modify_control: function(layer) {
        for (var i = 0; i < layer.controls.length; i++) {
            if (layer.controls[i].CLASS_NAME == 'OpenLayers.Control.ModifyFeature') {
                modify_control = layer.controls[i];
                modify_control.activate();
            }
            else if (layer.controls[i].active) {
                // Deactivate the non-modify control
                layer.controls[i].deactivate();
            }
        }
    },

    _get_editing_layer: function(map) {
        for (var i = 0; i < map.controls.length; i++) {
            if (map.controls[i] && map.controls[i].CLASS_NAME == 
                "olwidget.EditableLayerSwitcher") { 
                return map.vectorLayers[0];
            }
        }
    },

    _open_editing: function(map) {
        for (var i = 0; i < map.controls.length; i++) { 
            if (map.controls[i] && map.controls[i].CLASS_NAME == 
        "olwidget.EditableLayerSwitcher") { 
                layer = map.vectorLayers[0];
                if (layer.controls) {
                    this._remove_unneeded_controls(layer);
                    map.controls[i].setEditing(layer);

                    this._set_modify_control(layer);
                    this._registerEvents(map, layer);
                }
                break; 
            } 
        }
    },

    _remove_unneeded_controls: function(layer) {
        for (var i = 0; i < layer.controls.length; i++) { 
            if (layer.controls[i] && layer.controls[i].CLASS_NAME == 
        "OpenLayers.Control.Navigation") { 
                layer.controls.splice(i, 1);
                break; 
            } 
        }
    },
};
