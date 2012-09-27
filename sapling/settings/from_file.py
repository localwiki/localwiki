# Load custom settings from localsettings.py in DATA_ROOT.

from .defaults import *

 Where localsettings.py lives
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
