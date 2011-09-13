DEBUG = True

#######################################################################
# Config values you *must* change
#######################################################################

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'sapling',
        'USER': 'sapling',
        'PASSWORD': '** PASSWORD GOES HERE **',
        'HOST': '127.0.0.1',
    }
}

# Get an API key at http://cloudmade.com/start. Click on "Web" then "Get an API Key."
CLOUDMADE_API_KEY = 'SET THIS TO THE KEY YOU GET'

# Use these email settings when running the python debugging smtp server
# python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 1025
EMAIL_USE_TLS = False

#######################################################################
# Other config values.
#######################################################################

SITE_THEME = 'sapling'

OLWIDGET_DEFAULT_OPTIONS = {
    'default_lat': 37.76,
    'default_lon': -122.43,
    'default_zoom': 12,

    'layers': ['cloudmade.35165'],
    'map_options': {
        'controls': ['Navigation', 'PanZoomBar', 'KeyboardDefaults'],
        'theme': '/static/openlayers/theme/sapling/style.css',
    },
    'overlay_style': {'fillColor': '#ffc868',
                      'strokeColor': '#db9e33',
                      'strokeDashstyle': 'solid'},
    'map_div_class': 'mapwidget',
}

DAISYDIFF_URL = 'http://localhost:8080/daisydiff/diff'
DAISYDIFF_MERGE_URL = 'http://localhost:8080/daisydiff/merge'

# list of regular expressions for white listing embedded URLs
EMBED_ALLOWED_SRC = ['.*']

HAYSTACK_SOLR_URL = 'http://localhost:8080/solr'

LOCAL_INSTALLED_APPS = ()

CACHE_BACKEND = 'dummy:///'
