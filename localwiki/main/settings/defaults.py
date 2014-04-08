# Django settings for localwiki project.
import sys
import os

_ = lambda s: s

# By default, let's turn DEBUG on.  It should be set to False in
# localsettings.py.  We leave it set to True here so that our
# init_data_dir command can run correctly.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATA_ROOT = os.environ.get('LOCALWIKI_DATA_ROOT') or \
    os.path.join(sys.prefix, 'share', 'localwiki')

_settings_package_path = os.path.dirname(__file__)
PROJECT_ROOT = os.environ.get('LOCALWIKI_PROJECT_ROOT') or \
    os.path.join(os.path.dirname(_settings_package_path), '..')

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

SOUTH_MIGRATION_MODULES = {
    # HACK: South treats 'database' as the name of constance.backends.database
    'database': 'migrations.south.constance',
}

GLOBAL_LICENSE_NOTE = _("""<p>Except where otherwise noted, this content is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/3.0/">Creative Commons Attribution License</a>. See <a href="/Copyrights">Copyrights</a>.</p>""")

EDIT_LICENSE_NOTE = _("""<p>By clicking "Save Changes" you are agreeing to release your contribution under the <a rel="license" href="http://creativecommons.org/publicdomain/zero/1.0/" target="_blank">CC0 Public Domain license</a>, unless noted otherwise. See <a href="/Copyrights" target="_blank">Copyrights</a>.</p>""")

SIGNUP_TOS = _("""I agree to release my contributions under the <a rel="license" href="http://creativecommons.org/publicdomain/zero/1.0/" target="_blank">CC0 Public Domain license</a>, unless noted otherwise. See <a href="/Copyrights" target="_blank">Copyrights</a>.""")

SUBSCRIBE_MESSAGE = _("""I would like to receive occasional updates about this project via email.""")

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)

# Languages LocalWiki has been translated into.
LANGUAGES = (
    ('en', _('English')),
    ('ja', _('Japanese')),
    ('fr', _('French')),
    ('es', _('Spanish')),
    ('de', _('German')),
    ('uk', _('Ukrainian')),
)

SITE_ID = 1

MAIN_REGION = 'main'

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

AUTHENTICATION_BACKENDS = (
    'users.backends.CaseInsensitiveModelBackend',
    'users.backends.RestrictiveBackend',
)

AUTH_PROFILE_MODULE = 'users.UserProfile'

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
USER_REGION_ADMIN_CAN_MANAGE = [
    'pages.models.Page',
    'page.models.PageFile',
    'maps.models.MapData',
    'redirects.models.Redirect',
]

# django-guardian setting
ANONYMOUS_USER_ID = -1

# By default we load only one map layer on most pages to speed up load
# times.
OLWIDGET_INFOMAP_MAX_LAYERS = 1

# Should we display user's IP addresses to non-admin users?
SHOW_IP_ADDRESSES = True

LOGIN_REDIRECT_URL = '/'

THUMBNAIL_BACKEND = 'utils.sorl_backends.AutoFormatBackend'

OL_API = STATIC_URL + 'openlayers/OpenLayers.js?tm=1348975452'
OLWIDGET_CSS = '%solwidget/css/sapling.css?tm=1317359250' % STATIC_URL
OLWIDGET_JS = '%solwidget/js/olwidget.js?tm=1317359250' % STATIC_URL
CLOUDMADE_API = '%solwidget/js/sapling_cloudmade.js?tm=1317359250' % STATIC_URL

# django-honeypot options
HONEYPOT_FIELD_NAME = 'content2'
HONEYPOT_USE_JS_FIELD = True
HONEYPOT_REDIRECT_URL = '/'

TASTYPIE_ALLOW_MISSING_SLASH = True

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
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

    "constance.context_processors.config",
)

MIDDLEWARE_CLASSES = (
    'utils.middleware.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'utils.middleware.SubdomainLanguageMiddleware',
    'regions.middleware.RedirectToLanguageSubdomainMiddleware',
    'utils.middleware.RequestURIMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'honeypot.middleware.HoneypotMiddleware',
    'versionutils.versioning.middleware.AutoTrackUserInfoMiddleware',
    'redirects.middleware.RedirectFallbackMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'utils.middleware.FetchFromCacheMiddleware',
    'utils.middleware.TrackPOSTMiddleware',
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
    'users.auth.UnsaltedSHA1PasswordHasher',  # For legacy imports
)

# Dummy cache - TODO: switch to memcached by default
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

ROOT_URLCONF = 'main.urls'

TEMPLATE_DIRS = (
    os.path.join(DATA_ROOT, 'templates'),
    os.path.join(PROJECT_ROOT, 'templates'),
)

SOUTH_TESTS_MIGRATE = True

INSTALLED_APPS = (
    # Django-provided apps
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.gis',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.humanize',
    #'django.contrib.staticfiles',

    # Other third-party apps
    'haystack',
    'celery_haystack',
    'olwidget',
    'registration',
    'sorl.thumbnail',
    'staticfiles',
    'guardian',
    'south',
    'rest_framework',
    'rest_framework.authtoken',
    'honeypot',
    'constance.backends.database',
    'constance',
    'django_extensions',
    'corsheaders',
    'django_gravatar',
    'endless_pagination',
    'follow',

    # Our apps
    'versionutils.versioning',
    'versionutils.diff',
    'ckeditor',
    'regions',
    'pages',
    'maps',
    'redirects',
    'tags',
    'users',
    'recentchanges',
    'search',
    'frontpage',
    'dashboard',
    'stars',
    'main.api',
    'main',
    'utils',
)

LOCAL_INSTALLED_APPS = ()
TEMPLATE_DIRS = ()

SITE_THEME = 'sapling'

REST_FRAMEWORK = {
    'PAGINATE_BY': 30,
    # Allow client to override, using `?limit=xxx`.
    'PAGINATE_BY_PARAM': 'limit',  
    # Maximum limit allowed when using `?limit=xxx`.
    'MAX_PAGINATE_BY': 100,
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend', 'rest_framework.filters.OrderingFilter',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': [
        # Combined, these allow only authenticated users to 
        # write via the API and non-authenticated users to read.
        'main.api.permissions.DjangoObjectPermissionsOrAnonReadOnly',
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    # Base API policies
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'main.api.renderers.LocalWikiAPIRenderer',
    ),
}

# Allow Cross-Origin Resource Sharing headers on API urls
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'

ENDLESS_PAGINATION_PER_PAGE = 50

# For testing, you can start the python debugging smtp server like so:
# sudo python -m smtpd -n -c DebuggingServer localhost:25
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False
TEMPLATED_EMAIL_TEMPLATE_DIR = ''

OLWIDGET_DEFAULT_OPTIONS = {
    'default_lat': 37,
    'default_lon': -99,
    'default_zoom': 3,
    'zoom_to_data_extent_min': 16,

    'layers': ['mblw', 've.aerial'],
    'map_options': {
        'controls': ['Navigation', 'PanZoom', 'KeyboardDefaults'],
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

HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'

CACHE_BACKEND = 'dummy:///'

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_DATABASE_CACHE_BACKEND = 'default'

CONSTANCE_CONFIG = {
    'GOOGLE_ANALYTICS_ID': ('', 'UA-* identifier to pass to GA _setAccount'),
    'GOOGLE_ANALYTICS_SUBDOMAINS': ('', 'Subdomain value to pass to GA _setDomainName'),
    'GOOGLE_ANALYTICS_MULTIPLE_TOPLEVEL_DOMAINS': ('', 'Truthy/Falsey value to trigger GA _setAllowLinker'),
}
