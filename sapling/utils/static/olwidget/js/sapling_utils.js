SaplingMap = {

    init_openlayers: function() {
        OpenLayers.Control.LayerSwitcher.prototype.roundedCorner = false;
        var base_initOptions = olwidget.Map.prototype.initOptions;
        /* Resize map to fit content area */
        olwidget.Map.prototype.initOptions = function(options) {
            var opts = base_initOptions.call(this, options) 
            var border_height = 0;
            var map_height = $(window).height() - $('#header').outerHeight() - $('#main_header').outerHeight() - $('#content_header').outerHeight() - $('#content_footer').outerHeight() - ($('#content_wrapper').outerHeight() - $('#content').outerHeight() - border_height);
            opts['mapDivStyle']['height'] = map_height + 'px';
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
        if(map.opts.dynamic)
            this.setup_dynamic_map(map);
        this._open_editing(map);
    },

    setup_dynamic_map: function(map) {
        var layer = map.vectorLayers[0];
        layer.dataExtent = map.getExtent();
        loadObjects = this._loadObjects;
        layer.events.register("moveend", null, function(evt) {
          if(evt.zoomChanged
             || !layer.dataExtent
             || !layer.dataExtent.containsBounds(map.getExtent()))
             loadObjects(map, layer);
        });
        layer.events.register("featureselected", null, function(evt) {
          var feature = evt.feature;
          map.zoomToExtent(feature.geometry.bounds);
          map.deleteAllPopups();
          $('#header_title_detail').empty().append(' for ' + feature.attributes.html);
          var zoomedStyle = $.extend({}, 
              layer.styleMap.styles.select.defaultStyle,
              { fillOpacity: '0', strokeDashstyle: 'dash' });
          if(feature.geometry.CLASS_NAME != "OpenLayers.Geometry.Point")
              feature.style = zoomedStyle;
          loadObjects(map,layer,feature);
        });
        layer.events.register("featureunselected", null, function(evt) {
          evt.feature.style = layer.styleMap.styles['default'].defaultStyle;
          layer.drawFeature(evt.feature);
        })
    },

    _loadObjects: function(map, layer, selectedFeature) {
        var extent = map.getExtent().scale(1.5);
        var bbox = extent.clone().transform(layer.projection,
                       new OpenLayers.Projection('EPSG:4326')).toBBOX();
              
        var zoom = map.getZoom();
        $.get('_objects/', { 'bbox': bbox, 'zoom': zoom }, function(data){
            layer.dataExtent = extent;
            var temp = new olwidget.InfoLayer(eval(data));
            temp.visibility = false;
            map.addLayer(temp);
            layer.removeAllFeatures();
            map.deleteAllPopups();
            if(selectedFeature)
              layer.addFeatures(selectedFeature);
            var viewedArea = map.getExtent().toGeometry().getArea();
            $.each(temp.features, function(index, feature) {
              if(selectedFeature && selectedFeature.geometry.toString() == feature.geometry.toString())
                return;
              if(feature.geometry.CLASS_NAME == "OpenLayers.Geometry.Polygon")
              {
                var alpha =  0.5 - 0.5 * Math.min(1, feature.geometry.getArea()/viewedArea);
                var polyStyle = $.extend({}, 
                                  layer.styleMap.styles['default'].defaultStyle,
                                  { fillOpacity: alpha });
                feature.style = polyStyle;
              }
              layer.addFeatures(feature);
            });
            map.removeLayer(temp);
        })
    },

    _registerEvents: function(map, layer) {
        // Switch to "modify" mode after adding a feature.
        var self = this;
        layer.events.register("featureadded", null, function () {
                self._set_modify_control(layer);
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
