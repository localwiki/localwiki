/* This is essentially our local cloudmade API configuration.
 * Ideally we wouldn't have this here, but olwidget doesn't allow us to
 * pass in initialization paramters right now and I don't want to modify
 * it anymore right now.
 * */

// Get path of currently executing file. 
// source: http://stackoverflow.com/questions/2255689/how-to-get-the-file-path-of-the-currenctly-executing-javascript-code
(function() {
    var scripts = document.getElementsByTagName("script");
    var __FILE__ = scripts[scripts.length - 1].src;
    window.CLOUDMADE_API_KEY = __FILE__.split("#")[1];
})()

// Adapted from example provided by CloudMade wiki:
// http://developers.cloudmade.com/wiki/openlayers-api/CloudMade_Tiles
OpenLayers.Layer.CloudMade = OpenLayers.Class(OpenLayers.Layer.TMS, {
    initialize: function(name, options) {
        var key = CLOUDMADE_API_KEY;

        options = OpenLayers.Util.extend({
            attribution: "&copy; <a href=\"http://openstreetmap.org/\">OpenStreetMap</a> CC-BY-SA, &copy; <a href=\"http://cloudmade.com\">CloudMade</a>",
            maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
            maxResolution: 156543.0339,
            units: "m",
            projection: "EPSG:900913",
			isBaseLayer: true,
			numZoomLevels: 19,
			displayOutsideMaxExtent: true,
			wrapDateLine: true,
			styleId: 1,
            transitionEffect: 'resize'
        }, options);
		var prefix = [key, options.styleId, 256].join('/') + '/';
        var url = [
            "http://a.tile.cloudmade.com/" + prefix,
            "http://b.tile.cloudmade.com/" + prefix,
            "http://c.tile.cloudmade.com/" + prefix
        ];
        var newArguments = [name, url, options];
        OpenLayers.Layer.TMS.prototype.initialize.apply(this, newArguments);
    },

    getURL: function (bounds) {
        var res = this.map.getResolution();
        var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        var y = Math.round((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
        var z = this.map.getZoom();
        var limit = Math.pow(2, z);

        if (y < 0 || y >= limit)
        {
            return "http://cloudmade.com/js-api/images/empty-tile.png";
        }
        else
        {
            x = ((x % limit) + limit) % limit;

            var url = this.url;
            var path = z + "/" + x + "/" + y + ".png";

            if (url instanceof Array)
            {
                url = this.selectUrl(path, url);
            }

            return url + path;
        }
    },

    CLASS_NAME: "OpenLayers.Layer.CloudMade"
});

// CachedCloudMade is the same as CloudMade, except we require a URL
// parameter when the object is constructed.  The URL is expected to
// point to tiles in cloudmade's ZXY.png format and already have the
// required API key, style id, and size in it.  E.g.:
// http://a.tile.map.localwiki.org/ca694687020d468283a545db191bcb81/35165/256/
OpenLayers.Layer.CachedCloudMade = OpenLayers.Class(OpenLayers.Layer.CloudMade, {
    // Our initialize method requires a URL parameter.
    initialize: function(name, url, options) {
        options = OpenLayers.Util.extend({
            attribution: "&copy; <a href=\"http://openstreetmap.org/\">OpenStreetMap</a> CC-BY-SA, &copy; <a href=\"http://cloudmade.com\">CloudMade</a>",
            maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
            maxResolution: 156543.0339,
            units: "m",
            projection: "EPSG:900913",
			isBaseLayer: true,
			numZoomLevels: 19,
			displayOutsideMaxExtent: true,
			wrapDateLine: true,
			styleId: 1,
            transitionEffect: 'resize'
        }, options);
        var newArguments = [name, url, options];
        OpenLayers.Layer.TMS.prototype.initialize.apply(this, newArguments);
    },

    CLASS_NAME: "OpenLayers.Layer.CachedCloudMade"
});
