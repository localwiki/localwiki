#!/usr/bin/python
import os
import sys

from django.core.management import execute_manager, setup_environ

from utils.management.commands import init_data_dir, init_db

try:
    import settings  # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)


def data_dir_command():
    # Have to init django settings directly.
    setup_environ(settings)
    c = init_data_dir.Command()
    c.stderr = sys.stderr
    c.stdout = sys.stdout
    c.handle()


def db_init_command():
    # Have to init django settings directly.
    setup_environ(settings)
    c = init_db.Command()
    c.stderr = sys.stderr
    c.stdout = sys.stdout
    c.handle()


def main(set_apps_path=True):
    if set_apps_path:
        # Add local apps path.
        apps_path = os.path.split(os.path.abspath(__file__))[0]
        if apps_path not in sys.path:
            sys.path.append(apps_path)

    if len(sys.argv) >= 2:
        if sys.argv[1] == 'init_data_dir':
            # We have to special-case this command, as it happens before the
            # install's localsettings.py are installed, so the usual django
            # management machinery will throw errors about settings not
            # being set yet.
            data_dir_command()
            return
        elif sys.argv[1] == 'init_db':
            # We have to special-case this command, as it happens before the
            # install's localsettings.py are installed, so the usual django
            # management machinery will throw errors about settings not
            # being set yet.
            db_init_command()
            return

    execute_manager(settings)

if __name__ == "__main__":
    main(set_apps_path=False)
