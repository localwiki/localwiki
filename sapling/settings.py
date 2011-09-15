# Django settings for sapling project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

import os
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# staticfiles settings
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash. For integration with staticfiles, this should be the same as
# STATIC_URL followed by 'admin/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

AUTHENTICATION_BACKENDS = (
    'sapling.users.backends.CaseInsensitiveModelBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Should we display user's IP addresses to non-admin users?
SHOW_IP_ADDRESSES = True

LOGIN_REDIRECT_URL = '/'

HAYSTACK_SITECONF = 'sapling.search_sites'
HAYSTACK_SEARCH_ENGINE = 'solr'

OL_API = STATIC_URL + 'openlayers/OpenLayers.js'
OLWIDGET_CSS = '%solwidget/css/sapling.css' % STATIC_URL
CLOUDMADE_API = '%solwidget/js/sapling_cloudmade.js' % STATIC_URL

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "utils.context_processors.sites.current_site",

    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.csrf",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'versionutils.versioning.middleware.AutoTrackUserInfoMiddleware',
)

ROOT_URLCONF = 'sapling.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    # Django-provided apps
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.gis',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # Other third-party apps
    'haystack',
    'olwidget',
    'registration',
    'sorl.thumbnail',

    # Our apps
    'versionutils.versioning',
    'versionutils.diff',
    'ckeditor',
    'pages',
    'maps',
    'users',
    'recentchanges',
    'search',
    'utils',
)

try:
    from localsettings import *
except:
    pass

# Allow localsettings.py to define LOCAL_INSTALLED_APPS.
INSTALLED_APPS = tuple(list(INSTALLED_APPS) + list(LOCAL_INSTALLED_APPS))

# A site theme uses a template directory with a particular name.
THEME_TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'themes', SITE_THEME, 'templates')
TEMPLATE_DIRS = tuple(list(TEMPLATE_DIRS) + [THEME_TEMPLATE_DIR])

# A site theme uses a static assets directory with a particular name.
STATICFILES_DIRS = (
    ('theme', os.path.join(PROJECT_ROOT, 'themes', SITE_THEME, 'assets')),
)

# Generate a local secret key.
if not 'SECRET_KEY' in locals():
    from random import choice
    SECRET_KEY = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
    fname = os.path.join(os.path.dirname(__file__), 'localsettings.py')
    f = open(fname, 'a')
    f.write("SECRET_KEY = '%s'" % SECRET_KEY)
    f.close()
