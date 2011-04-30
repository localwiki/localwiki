SaplingMap = {

    init_openlayers: function() {
        OpenLayers.Control.LayerSwitcher.prototype.roundedCorner = false;
        var base_initOptions = olwidget.Map.prototype.initOptions;
        /* Resize map to fit content area */
        olwidget.Map.prototype.initOptions = function(options) {
            var opts = base_initOptions.call(this, options) 
            var map_height = $(window).height() - $('#header').height() - $('#main_header').height() - $('#content_header').height();
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
        this._open_editing(map);    
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
                    //console.dir(layer.controls);
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
