SaplingMap = {

    is_dirty: false,

    init_openlayers: function() {
        OpenLayers.Control.LayerSwitcher.prototype.roundedCorner = false;
        OpenLayers.IMAGE_RELOAD_ATTEMPTS = 5;
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
        /* Set the render default to Canvas rather than SVG */
        OpenLayers.Layer.Vector.prototype.renderers = ['Canvas', 'SVG', 'VML'];

        SaplingMap._setup_clustering_strategy();

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
        };
        /* We don't want a permalinked URL until they move the map */
        OpenLayers.Control.Permalink.prototype.draw = function () {
            OpenLayers.Control.prototype.draw.apply(this, arguments);
            this.map.events.on({
                'moveend': this.updateLink,
                'changelayer': this.updateLink,
                'changebaselayer': this.updateLink,
                scope: this
            });
            return this.div;
        };
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

        if(map.opts.permalink) {
            map.addControl(new OpenLayers.Control.Permalink({anchor: true}));
        }

        this.setup_link_hover_activation(map);
    },

    setup_link_hover_activation: function(map) {
        var layer = map.vectorLayers[0];
        var url_to_features = {};
        $.each(layer.features, function(index, feature) {
            // Find URL in html.
            var quoted = /"(.*?)"/;
            var quoted_match = quoted.exec(feature.attributes.html);
            if (quoted_match) {
                var url = quoted.exec(feature.attributes.html)[1];
                url_to_features[url] = feature;
            }
        })

        $('#content a').each(function() {
            var feature = url_to_features[$(this).attr('href')];
            $(this).bind('mouseover', function (){
                SaplingMap._highlightResult(this, feature, map, true);
            });
        });
    },

    _set_selected_style: function(map, feature) {
        var viewedArea = map.getExtent().toGeometry().getArea();
        var area_ratio = Math.min(1, feature.geometry.getArea()/viewedArea);
        var fillAlpha =  0.2 - 0.2 * area_ratio;
        // Always have some stroke for selected features.
        var strokeAlpha = Math.max(0.2, 1 - 1 * area_ratio);
        var strokeWidth = Math.max(2, 15 * area_ratio);
        var zoomedStyle = $.extend({}, 
            layer.styleMap.styles['select'].defaultStyle,
            { fillOpacity: fillAlpha,
              // TODO: Not sure why we need to specify strokeWidth
              // here.
              strokeWidth: strokeWidth, strokeOpacity: strokeAlpha,
              label: null });
        if(feature.geometry.CLASS_NAME != "OpenLayers.Geometry.Point")
          {
              feature.style = zoomedStyle;
              layer.drawFeature(feature);
          }
    },

    _setup_dynamic_events: function(map, layer) {
        loadObjects = this._loadObjects
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
          var selectedFeature = layer.selectedFeatures && layer.selectedFeatures[0];
          // Hack to maintain selected feature state throughout events.
          // Not sure why this is required.
          layer._selectedFeature = selectedFeature;
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
          if (selectedFeature.cluster)
            var feature_label = selectedFeature.cluster[0].attributes.html;
          else
            var feature_label = selectedFeature.attributes.html;
          $('#header_title_detail').empty().append(gettext(' for ') + feature_label);

          SaplingMap._set_selected_style(map, feature);
          displayRelated(map);
        });
        layer.events.register("featureunselected", null, function(evt) {
          // Hack to maintain selected feature state throughout events.
          // Not sure why this is required.
          layer._selectedFeature = null;
          SaplingMap._set_feature_alpha(evt.feature, layer, map);
          layer.drawFeature(evt.feature);
          $('#header_title_detail').empty();
        })
    },

    setup_dynamic_map: function(map, layer) {
        if (!layer) {
            var layer = map.vectorLayers[0];
        }
        
        layer.dataExtent = map.getExtent();
        var set_feature_alpha = SaplingMap._set_feature_alpha;
        var is_feature_invisible = SaplingMap._is_feature_invisible;
        var invisible_features = [];
        $.each(layer.features, function(index, feature) {
           set_feature_alpha(feature, layer, map);
           if (is_feature_invisible(feature, layer, map))
               invisible_features.push(feature);
        });
        layer.redraw();
        if (invisible_features)
            layer.removeFeatures(invisible_features);

        this._setup_dynamic_events(map, layer);
    },

    beforeUnload: function(e) {
        if(SaplingMap.is_dirty) {
            return e.returnValue = gettext("You've made changes but haven't saved.  Are you sure you want to leave this page?");
        }
    },

    _set_feature_alpha: function(feature, layer, map) {
        if (!feature)
            return;
        var viewedRegion = map.getExtent().toGeometry();
        if(feature.geometry.CLASS_NAME == "OpenLayers.Geometry.Polygon")
        {
            var area_ratio = Math.min(1, feature.geometry.getArea()/viewedRegion.getArea());
            var fillAlpha =  0.5 - 0.5 * area_ratio;
            var strokeAlpha = 1 - 1 * area_ratio;
            var strokeWidth = Math.max(2, 15 * area_ratio);

            var polyStyle = $.extend({},
                layer.styleMap.styles['default'].defaultStyle,
                // TODO: Not sure why we have to explicitly set
                // strokeWidth and label here. It's like we need to somehow pass
                // the variables' context in but I couldn't figure out
                // how.
                { fillOpacity: fillAlpha, strokeOpacity: strokeAlpha, strokeWidth: strokeWidth, label: null });
            feature.style = polyStyle;
        }
        else if(feature.geometry.CLASS_NAME == "OpenLayers.Geometry.LineString")
        {
            var length_ratio = Math.min(1, feature.geometry.getLength()/viewedRegion.getLength());
            var strokeAlpha = 0.5; //1 - 1 * length_ratio;
            var strokeWidth = 2; //Math.max(2, 15 * length_ratio);

            var lineStyle = $.extend({},
                layer.styleMap.styles['default'].defaultStyle,
                // TODO: Not sure why we have to explicitly set
                // strokeWidth and label here. It's like we need to somehow pass
                // the variables' context in but I couldn't figure out
                // how.
                { strokeOpacity: strokeAlpha, strokeWidth: strokeWidth, label: null });
            feature.style = lineStyle;
        }
    },

    _is_feature_invisible: function(feature, layer, map) {
        var viewedRegion = map.getExtent().toGeometry();
        if (!feature)
            return
        if(feature.geometry.CLASS_NAME == "OpenLayers.Geometry.Polygon") {
            if ((feature.geometry.getArea()/viewedRegion.getArea()) >= 1) {
                return true;
            }
        }
    },

    _highlightResult: function (result, feature, map, is_inside_page) {
            var lonlat = feature.geometry.getBounds().getCenterLonLat();
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
            feature.style = $.extend({}, layer.styleMap.styles['select'].defaultStyle, {label: null});
            layer.drawFeature(feature);
            $(result).bind('mouseout', function(){
                $(this).unbind('mouseout');
                map.removePopup(popup);
                feature.style = feature.defaultStyle;
                if (is_inside_page) {
                    feature.style = $.extend({}, layer.styleMap.styles['default'].defaultStyle, {label: null});
                    layer.drawFeature(feature);
                }
                else {
                    // Points are clustered, so we erase the feature to
                    // prevent the non-clustered point from being drawn.
                    if (feature.geometry.CLASS_NAME == "OpenLayers.Geometry.Point") {
                        layer.eraseFeatures(feature);
                    }
                    else {
                        layer.drawFeature(feature);
                        // Keep the selected feature on top of other
                        // features after they've been drawn.
                        if (layer._selectedFeature) {
                            layer.eraseFeatures([layer._selectedFeature]);
                            SaplingMap._set_selected_style(map, layer._selectedFeature);
                        }
                    }
                }
                if(existingPopup)
                    map.addPopup(existingPopup);
            });
    },

    _displayRelated: function(map) {
        var layer = map.vectorLayers[0];
        
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
        var header = gettext('Things on this map:');
        var results = $('<ol>');
        var set_feature_alpha = SaplingMap._set_feature_alpha;
        var is_feature_invisible = SaplingMap._is_feature_invisible;
        var invisible_features = [];
        $.each(layer.features, function(index, feature) {
           if(feature == selectedFeature)
                return;
           if (is_feature_invisible(feature, layer, map)) {
               invisible_features.push(feature);
           }
           var listResult = false;
           if(selectedFeature)
           {
               if(selectedFeature.geometry.CLASS_NAME == "OpenLayers.Geometry.Polygon")
               {
                   header = gettext('Things inside ') + selectedFeature.attributes.html + ':';
                   $.each(feature.geometry.getVertices(), function(ind, vertex){
                       if(selectedFeature.geometry.containsPoint(vertex))
                       {
                           listResult = true;
                           return false;
                       }
                   });
               } else {
                   var threshold = 500; // TODO: what units is this?
                   if (selectedFeature.cluster)
                       var feature_label = selectedFeature.cluster[0].attributes.html;
                   else
                       var feature_label = selectedFeature.attributes.html;
                   header = gettext('Things near ') + feature_label + ':';
                   listResult = selectedFeature.geometry.distanceTo(feature.geometry) < threshold;
               }
           }
           if(listResult || !selectedFeature)
           {
               var feature_items = [feature];
               if (feature.cluster) {
                 feature_items = feature.cluster;
               }
               $.each(feature_items, function(index, feature) {
                  var result = $('<li class="map_result">')
                               .html(feature.attributes.html)
                               .bind('mouseover', function (){
                                   SaplingMap._highlightResult(this, feature, map);
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
               });
           }
        });
        if (invisible_features)
            layer.removeFeatures(invisible_features);
        $('#results_pane').empty().append($('<h3/>').html(header)).append(results);
    },

    _format_bbox_data: function(data) {
        for (var i=0; i<data.length; i++) {
            var item = data[i];
            var slug = encodeURIComponent(item[1].replace(' ', '_'));
            var page_url = '/' + slug;
            data[i][1] = '<a href="' + page_url + '">' + item[1] + '</a>';
        }
        return data;
    },

    _loadObjects: function(map, layer, callback) {
        var selectedFeature = layer._selectedFeature;
        var extent = map.getExtent().scale(1.5);
        var bbox = extent.clone().transform(layer.projection,
                       new OpenLayers.Projection('EPSG:4326')).toBBOX();
        var zoom = map.getZoom();
        var set_feature_alpha = SaplingMap._set_feature_alpha;
        var myDataToken = Math.random();
        layer.dataToken = myDataToken;

        $.get('_objects/', { 'bbox': bbox, 'zoom': zoom }, function(data){
            if(layer.dataToken != myDataToken)
            {
                return;
            }
            layer.dataExtent = extent;

            // Turn off clustering before fiddling with the layer.
            layer.strategies[0].deactivate();

            var temp = new olwidget.InfoLayer(SaplingMap._format_bbox_data(data));
            temp.visibility = false;
            map.addLayer(temp);
            layer.removeAllFeatures();

            $.each(temp.features, function(index, feature) {
                if(selectedFeature && selectedFeature.geometry.toString() == feature.geometry.toString()) {
                    temp.features[index] = selectedFeature;
                    SaplingMap._set_selected_style(map, selectedFeature);
                }
                else {
                    set_feature_alpha(feature, temp, map);
                }
            });

            layer.addFeatures(temp.features);
            if (selectedFeature)
                layer.selectedFeatures = [selectedFeature];
            map.removeLayer(temp);

            // Turn clustering back on.
            layer.strategies[0].activate();

            if(callback){
                callback();
            }
        })
    },

    _register_edit_events: function(map, layer) {
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
                    this._register_edit_events(map, layer);
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

    // Our custom OpenLayers clustering logic. This is the usual Cluster strategy except we ignore
    // polygons and lines.  TODO: move this to a separate file.
    _setup_clustering_strategy: function() {

        var base_shouldCluster = OpenLayers.Strategy.Cluster.prototype.shouldCluster;
        OpenLayers.Strategy.Cluster.prototype.shouldCluster = function(cluster, feature) {
            if (feature.geometry.CLASS_NAME == "OpenLayers.Geometry.Point") {
                return base_shouldCluster.call(this, cluster, feature);
            }
            return false;
        };
        
        OpenLayers.Strategy.Cluster.prototype.cluster = function(event) {
        
            if((!event || event.zoomChanged) && this.features) {
                var resolution = this.layer.map.getResolution();
                if(resolution != this.resolution || !this.clustersExist()) {
                    this.resolution = resolution;
                    var clusters = [];
                    var feature, clustered, cluster;
                    for(var i=0; i<this.features.length; ++i) {
                        feature = this.features[i];
                        if(feature.geometry) {
                            clustered = false;
                            for(var j=clusters.length-1; j>=0; --j) {
                                cluster = clusters[j];
                                if(this.shouldCluster(cluster, feature)) {
                                    this.addToCluster(cluster, feature);
                                    clustered = true;
                                    break;
                                }
                            }
                            if(!clustered) {
                                if(this.features[i].geometry.CLASS_NAME == "OpenLayers.Geometry.Point") {
                                   clusters.push(this.createCluster(this.features[i]));
                                }
                                else {
                                   var cluster = this.features[i];
                                   cluster.cluster = [this.features[i]];
                                   clusters.push(cluster);
                                }
                            }
                        }
                    }
                    this.layer.removeAllFeatures();
                    if(clusters.length > 0) {
                        if(this.threshold > 1) {
                            var clone = clusters.slice();
                            clusters = [];
                            var candidate;
                            for(var i=0, len=clone.length; i<len; ++i) {
                                candidate = clone[i];
                                if(candidate.attributes.count < this.threshold) {
                                    Array.prototype.push.apply(clusters, candidate.cluster);
                                } else {
                                    clusters.push(candidate);
                                }
                            }
                        }
                        this.clustering = true;
                        // A legitimate feature addition could occur during this
                        // addFeatures call.  For clustering to behave well, features
                        // should be removed from a layer before requesting a new batch.
                        this.layer.addFeatures(clusters);
                        this.clustering = false;
                    }
                    this.clusters = clusters;
                }
            }
        }
    },
};
