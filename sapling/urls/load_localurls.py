# Load custom urls from localurls.py in DATA_ROOT.

from .defaults import *
from settings import DATA_ROOT
import sys
import os

# Where localurls.py lives
sys.path.append(os.path.join(DATA_ROOT, 'conf'))
try:
    from localurls import *
except:
    pass


# Allow localurls.py to define localurlpatterns.
if localurlpatterns is not None:
    urlpatterns = localurlpatterns + urlpatterns
