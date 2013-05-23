# Load custom settings from localsettings.py in DATA_ROOT. Update the
# settings based on the chosen SITE_THEME and any LOCAL_INSTALLED_APPS.

from .defaults import *
from .includes.theme import theme_template_dirs, theme_staticfiles_dirs

# Where localsettings.py lives
sys.path.append(os.path.join(DATA_ROOT, 'conf'))
try:
    from localsettings import *
except:
    pass


# Allow localsettings.py to define LOCAL_INSTALLED_APPS.
INSTALLED_APPS = tuple(list(INSTALLED_APPS) + list(LOCAL_INSTALLED_APPS))

TEMPLATE_DIRS = theme_template_dirs([DATA_ROOT, PROJECT_ROOT], SITE_THEME) + list(TEMPLATE_DIRS)
STATICFILES_DIRS = theme_staticfiles_dirs([DATA_ROOT, PROJECT_ROOT], SITE_THEME)
