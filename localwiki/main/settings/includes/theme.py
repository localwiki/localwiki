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

def theme_staticfiles_dirs(root_dirs, site_theme):
	# Returns a list of assets/ directories inside of theme folders in
	# root_dirs as described above.
	asset_dirs = [os.path.join(root_dir, 'themes', site_theme, 'assets') for
		root_dir in root_dirs]
	return [('theme', asset_dir) for asset_dir in asset_dirs if
		os.path.exists(asset_dir)]
