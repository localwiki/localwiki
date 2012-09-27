import os.path


def theme_template_dirs(DATA_ROOT, PROJECT_ROOT, SITE_THEME):
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

	return [LOCAL_TEMPLATE_DIR, PROJECT_TEMPLATE_DIR, LOCAL_THEME_TEMPLATE_DIR,
		PROJECT_THEME_TEMPLATE_DIR]


def theme_staticfiles_dirs(DATA_ROOT, PROJECT_ROOT, SITE_THEME):
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
	return STATICFILES_DIRS
