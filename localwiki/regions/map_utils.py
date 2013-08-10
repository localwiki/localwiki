def get_zoom_for_extent(extent):
    # Viewport values pulled from map size on full screen
    # on Philip's MacbookAir 11".
    view_x = 1251
    view_y = 293

    bbox = extent.coords[0]
    bbox_width = (bbox[1][0] - bbox[0][0]) * 100000
    bbox_height = (bbox[2][1] - bbox[1][1]) * 100000
    ideal_resolution = max(
        bbox_width / view_x,
        bbox_height / view_y
    )
    return get_zoom_for_resolution(ideal_resolution)

# Obtain this by adding:
# console.log(this.resolutions)
# to getExtent() in Layer.js in OpenLayers.js
# and I added two more smaller resolutions.
map_viewport_resolutions = [
    156543.03390625,
    78271.516953125,
    39135.7584765625,
    19567.87923828125,
    9783.939619140625,
    4891.9698095703125,
    2445.9849047851562,
    1222.9924523925781,
    611.4962261962891,
    305.74811309814453,
    152.87405654907226,
    76.43702827453613,
    38.218514137268066,
    19.109257068634033,
    9.554628534317017,
    4.777314267158508,
    2.388657133579254,
    1.194328566789627
]

def get_zoom_for_resolution(resolution):
    for i, view_resolution in enumerate(map_viewport_resolutions):
        n = i
        if resolution >= view_resolution:
            break
    return max(0, n - 1)
