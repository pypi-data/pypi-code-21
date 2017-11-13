"""
This module support both Python 2.7 and 3 by handling importing packages
either unsupported or moved between Python versions
"""

############################
# StringIO
############################
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
