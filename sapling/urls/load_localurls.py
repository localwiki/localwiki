# Load custom urls from localurls.py in DATA_ROOT.

from .defaults import *
import sys, os

# Where localurls.py lives
sys.path.append(os.path.join(DATA_ROOT, 'conf'))
try:
    from localurls import *
except:
    pass


# Allow localurls.py to define localurlpatterns.
urlpatterns = localurlpatterns + urlpatterns
