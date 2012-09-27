import os.path


def theme_template_dirs(root_dirs, site_theme):
	# root_dirs is a list of paths to folders containing templates
	# and/or themes, usually PROJECT_ROOT and DATA_ROOT.
	# A site theme uses a template directory with a particular name
	# inside of the themes/ directory in a root_dir.
	template_dirs = [os.path.join(root_dir, 'templates') for root_dir in root_dirs]
	theme_template_dirs = [
		os.path.join(root_dir, 'themes', site_theme, 'templates') for
			root_dir in root_dirs]
	return template_dirs + theme_template_dirs

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
