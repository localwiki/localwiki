# Django settings for sapling project.
import sys
import os

# By default, let's turn DEBUG on.  It should be set to False in
# localsettings.py.  We leave it set to True here so that our
# init_data_dir command can run correctly.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATA_ROOT = os.path.join(sys.prefix, 'share', 'localwiki')
PROJECT_ROOT = os.path.join(os.path.dirname(__file__))

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

GLOBAL_LICENSE_NOTE = """<p>Except where otherwise noted, this content is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/3.0/">Creative Commons Attribution License</a>. See <a href="/Copyrights">Copyrights.</p>"""

EDIT_LICENSE_NOTE = """<p>By clicking "Save Changes" you are agreeing to release your contribution under the <a rel="license" href="http://creativecommons.org/licenses/by/3.0/" target="_blank">Creative Commons-By license</a>, unless noted otherwise. See <a href="/Copyrights" target="_blank">Copyrights</a>.</p>"""

SIGNUP_TOS = """I agree to release my contributions under the <a rel="license" href="http://creativecommons.org/licenses/by/3.0/" target="_blank">Creative Commons-By license</a>, unless noted otherwise. See <a href="/Copyrights" target="_blank">Copyrights</a>."""

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
MEDIA_ROOT = os.path.join(DATA_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# staticfiles settings
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(DATA_ROOT, 'static')

# TODO: Temporary until we upgrade to the next Django release and have
# the latest staticfiles changes.
STATICFILES_FINDERS = (
    'staticfiles.finders.FileSystemFinder',
    'staticfiles.finders.AppDirectoriesFinder'
)

STATICFILES_STORAGE = 'staticfiles.storage.CachedStaticFilesStorage'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash. For integration with staticfiles, this should be the same as
# STATIC_URL followed by 'admin/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

AUTHENTICATION_BACKENDS = (
    'sapling.users.backends.CaseInsensitiveModelBackend',
    'sapling.users.backends.RestrictiveBackend',
)

# users app settings
USERS_ANONYMOUS_GROUP = 'Anonymous'
USERS_BANNED_GROUP = 'Banned'
USERS_DEFAULT_GROUP = 'Authenticated'
USERS_DEFAULT_PERMISSIONS = {'auth.group':
                                [{'name': USERS_DEFAULT_GROUP,
                                  'permissions':
                                    [['add_mapdata', 'maps', 'mapdata'],
                                     ['change_mapdata', 'maps', 'mapdata'],
                                     ['delete_mapdata', 'maps', 'mapdata'],
                                     ['add_page', 'pages', 'page'],
                                     ['change_page', 'pages', 'page'],
                                     ['delete_page', 'pages', 'page'],
                                     ['add_pagefile', 'pages', 'pagefile'],
                                     ['change_pagefile', 'pages', 'pagefile'],
                                     ['delete_pagefile', 'pages', 'pagefile'],
                                     ['add_redirect', 'redirects', 'redirect'],
                                     ['change_redirect', 'redirects', 'redirect'],
                                     ['delete_redirect', 'redirects', 'redirect'],
                                    ]
                                 },
                                 {'name': USERS_ANONYMOUS_GROUP,
                                  'permissions':
                                    [['add_mapdata', 'maps', 'mapdata'],
                                     ['change_mapdata', 'maps', 'mapdata'],
                                     ['delete_mapdata', 'maps', 'mapdata'],
                                     ['add_page', 'pages', 'page'],
                                     ['change_page', 'pages', 'page'],
                                     ['delete_page', 'pages', 'page'],
                                     ['add_pagefile', 'pages', 'pagefile'],
                                     ['change_pagefile', 'pages', 'pagefile'],
                                     ['delete_pagefile', 'pages', 'pagefile'],
                                     ['add_redirect', 'redirects', 'redirect'],
                                     ['change_redirect', 'redirects', 'redirect'],
                                     ['delete_redirect', 'redirects', 'redirect'],
                                    ]
                                 },
                                ]
                            }

# django-guardian setting
ANONYMOUS_USER_ID = -1

# By default we load only one map layer on most pages to speed up load
# times.
OLWIDGET_INFOMAP_MAX_LAYERS = 1

# Should we display user's IP addresses to non-admin users?
SHOW_IP_ADDRESSES = True

LOGIN_REDIRECT_URL = '/'

HAYSTACK_SITECONF = 'sapling.search_sites'
HAYSTACK_SEARCH_ENGINE = 'solr'

THUMBNAIL_BACKEND = 'utils.sorl_backends.AutoFormatBackend'

OL_API = STATIC_URL + 'openlayers/OpenLayers.js?tm=1317359250'
OLWIDGET_CSS = '%solwidget/css/sapling.css?tm=1317359250' % STATIC_URL
OLWIDGET_JS = '%solwidget/js/olwidget.js?tm=1317359250' % STATIC_URL
CLOUDMADE_API = '%solwidget/js/sapling_cloudmade.js?tm=1317359250' % STATIC_URL

# django-honeypot options
HONEYPOT_FIELD_NAME = 'content2'
HONEYPOT_USE_JS_FIELD = True
HONEYPOT_REDIRECT_URL = '/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "utils.context_processors.sites.current_site",
    "utils.context_processors.settings.license_agreements",

    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.csrf",
    "django.core.context_processors.media",
    #"django.core.context_processors.static",
    "staticfiles.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'honeypot.middleware.HoneypotMiddleware',
    'versionutils.versioning.middleware.AutoTrackUserInfoMiddleware',
    'redirects.middleware.RedirectFallbackMiddleware',
)

ROOT_URLCONF = 'sapling.urls'

TEMPLATE_DIRS = (
    os.path.join(DATA_ROOT, 'templates'),
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
    #'django.contrib.staticfiles',

    # Other third-party apps
    'haystack',
    'olwidget',
    'registration',
    'sorl.thumbnail',
    'staticfiles',
    'guardian',
    'south',
    'honeypot',

    # Our apps
    'versionutils.versioning',
    'versionutils.diff',
    'ckeditor',
    'pages',
    'maps',
    'users',
    'recentchanges',
    'search',
    'redirects',
    'utils',
)

LOCAL_INSTALLED_APPS = ()
# We set this manually, after localsettings import, below.
TEMPLATE_DIRS = ()

SITE_THEME = 'sapling'

# Where localsettings.py lives
sys.path.append(os.path.join(DATA_ROOT, 'conf'))
try:
    from localsettings import *
except:
    pass

# Allow localsettings.py to define LOCAL_INSTALLED_APPS.
INSTALLED_APPS = tuple(list(INSTALLED_APPS) + list(LOCAL_INSTALLED_APPS))

###############################
# Setup template directories
###############################
LOCAL_TEMPLATE_DIR = os.path.join(DATA_ROOT, 'templates')
PROJECT_TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')

# A site theme uses a template directory with a particular name.
# Site themes can live in either the global themes/ directory
# or in the local themes/ directory (in DATA_ROOT).
PROJECT_THEME_TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'themes', SITE_THEME, 'templates')
LOCAL_THEME_TEMPLATE_DIR = os.path.join(DATA_ROOT, 'themes', SITE_THEME, 'templates')

TEMPLATE_DIRS = tuple([LOCAL_TEMPLATE_DIR, PROJECT_TEMPLATE_DIR, LOCAL_THEME_TEMPLATE_DIR, PROJECT_THEME_TEMPLATE_DIR] +
                      list(TEMPLATE_DIRS))


STATICFILES_DIRS = []
# A site theme uses a static assets directory with a particular name.
# Site themes can live in either the global themes/ directory
# or in the local themes/ directory (in DATA_ROOT).
_local_theme_dir = os.path.join(DATA_ROOT, 'themes', SITE_THEME, 'assets')
_global_theme_dir = os.path.join(PROJECT_ROOT, 'themes', SITE_THEME, 'assets')
if os.path.exists(_local_theme_dir):
    STATICFILES_DIRS.append(('theme', _local_theme_dir))
if os.path.exists(_global_theme_dir):
    STATICFILES_DIRS.append(('theme', _global_theme_dir))
