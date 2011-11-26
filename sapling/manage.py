#!/usr/bin/python
import os
import site
import sys

# We have to hard-code these here, as we run a few setup commands (in
# setup_all) that execute before the settings can be safely loaded.
DATA_ROOT = os.path.join(sys.prefix, 'share', 'localwiki')
PROJECT_ROOT = os.path.split(os.path.abspath(__file__))[0]

# Add virtualenv packages
site_packages = os.path.join(DATA_ROOT, 'env', 'lib',
                    'python%s' % sys.version[:3], 'site-packages')
site.addsitedir(site_packages)

from django.core.management import execute_manager
from utils.management.commands import init_data_dir, init_db, init_settings


def main(set_apps_path=True):
    if set_apps_path:
        # Add local apps path.
        apps_path = os.path.split(os.path.abspath(__file__))[0]
        if apps_path not in sys.path:
            sys.path.append(apps_path)

    if len(sys.argv) >= 2 and sys.argv[1] == 'setup_all':
        # We have to special-case this commands, it happens before the
        # install's localsettings.py is installed, so the usual django
        # management machinery will throw errors about settings not
        # being set yet.  But after we have run the setup commands we
        # let it fall through to the normal django method.
        if not os.path.exists(os.path.join(DATA_ROOT, 'conf')):
            init_data_dir.run(DATA_ROOT=DATA_ROOT, PROJECT_ROOT=PROJECT_ROOT)
            init_db.run(DATA_ROOT=DATA_ROOT, PROJECT_ROOT=PROJECT_ROOT)
            init_settings.run(DATA_ROOT=DATA_ROOT, PROJECT_ROOT=PROJECT_ROOT)
        else:
            print "Existing localwiki data directory found! Using %s\n" % DATA_ROOT

    if len(sys.argv) >= 2:
        if sys.argv[1] == 'init_data_dir':
            init_data_dir.run(DATA_ROOT=DATA_ROOT, PROJECT_ROOT=PROJECT_ROOT)
            return
        if sys.argv[1] == 'init_db':
            init_db.run(DATA_ROOT=DATA_ROOT, PROJECT_ROOT=PROJECT_ROOT)
            return
        if sys.argv[1] == 'init_settings':
            init_settings.run(DATA_ROOT=DATA_ROOT, PROJECT_ROOT=PROJECT_ROOT)
            return

    try:
        import settings  # Assumed to be in the same directory.
    except ImportError:
        sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
        sys.exit(1)

    execute_manager(settings)

if __name__ == "__main__":
    main(set_apps_path=False)
