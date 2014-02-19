#!/usr/bin/python
import os
import site
import sys

# We have to hard-code these here, as we run a few setup commands (in
# setup_all) that execute before the settings can be safely loaded.
DATA_ROOT = os.environ.get('LOCALWIKI_DATA_ROOT') or \
    os.path.join(sys.prefix, 'share', 'localwiki')
PROJECT_ROOT = os.environ.get('LOCALWIKI_PROJECT_ROOT') or \
    os.path.split(os.path.abspath(__file__))[0]

# Add virtualenv packages
site_packages = os.path.join(DATA_ROOT, 'env', 'lib',
                    'python%s' % sys.version[:3], 'site-packages')
site.addsitedir(site_packages)

from django.core.management import execute_from_command_line


def main(set_apps_path=True):
    if set_apps_path:
        # Add local apps path.
        apps_path = os.path.split(os.path.abspath(__file__))[0]
        if apps_path not in sys.path:
            sys.path.append(apps_path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main(set_apps_path=False)
