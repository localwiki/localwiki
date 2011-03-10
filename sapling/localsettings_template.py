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

DAISYDIFF_URL = 'http://localhost:8080/diff'
DAISYDIFF_MERGE_URL = 'http://localhost:8080/merge'

LOCAL_INSTALLED_APPS = ()
