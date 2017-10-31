from . import backups

import sys

if sys.version_info < (3, 0):
    from urlparse import urlparse
else:
    from urllib.parse import urlparse
