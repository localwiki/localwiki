"""
This module is imported after the server is started. It's intended to be
used to call -- or import modules that call -- various register() methods.
"""

import api
import feeds
import signals
