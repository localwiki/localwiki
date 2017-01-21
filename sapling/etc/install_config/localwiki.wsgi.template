# This is an example .wsgi file that will work if you've installed
# localwiki globally, e.g. via apt-get.

import os
import sys

# WSGI has undefined behavior for stdout. This fixes issues with some external
# libraries printing to sys.stdout.
sys.stdout = sys.stderr

# Add virtualenv path.
from sapling import manage

# Add local apps path.
apps_path = os.path.abspath(os.path.join(manage.__file__, '..'))
if apps_path not in sys.path:
    sys.path.append(apps_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'sapling.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
