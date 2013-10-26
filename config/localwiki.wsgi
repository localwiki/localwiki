# This is an example .wsgi file for serving up localwiki inside of a
# custom virtualenv.
#
#############################################################
# CHANGE THIS LINE to the absolute path of the virtualenv:
#############################################################
VIRTUAL_ENV_PATH = '{{ virtualenv }}'

import os
import sys

# WSGI has undefined behavior for stdout. This fixes issues with some external
# libraries printing to sys.stdout.
sys.stdout = sys.stderr

activate_this = os.path.join(VIRTUAL_ENV_PATH, 'bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

import localwiki

# Add local apps path.
apps_path = os.path.split(os.path.abspath(localwiki.__file__))[0]
if apps_path not in sys.path:
    sys.path.append(apps_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "localwiki.main.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
