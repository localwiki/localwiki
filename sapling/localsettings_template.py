DEBUG = True
CACHE_BACKEND = 'dummy:///'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'sapling',
        'USER': 'sapling',
        'PASSWORD': '** PASSWORD GOES HERE **',
        'HOST': '127.0.0.1',
    }
}

OLWIDGET_DEFAULT_OPTIONS = {
    'default_lat': 37.76,
    'default_lon': -122.43,
    'default_zoom': 12,

    'layers': ['cloudmade.33813'],
    'map_options': {
        'controls': ['Navigation', 'LayerSwitcher', 'PanZoomBar',
                     'Attribution'],
        'theme': '/static/openlayers/theme/sapling/style.css',
    },
    'overlay_style': {'fillColor': '#ffc868',
                      'strokeColor': '#db9e33'},
}

DAISYDIFF_URL = 'http://localhost:8080/diff'
DAISYDIFF_MERGE_URL = 'http://localhost:8080/merge'

LOCAL_INSTALLED_APPS = ()

CLOUDMADE_API_KEY = 'Get an API key at http://cloudmade.com'
