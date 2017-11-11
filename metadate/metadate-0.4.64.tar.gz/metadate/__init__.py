""" You can kind of see this as the scope of `metadate` when you 'import metadate'
The following functions become available:
metadate.__project__
metadate.__version__
metadate.print_version
metadate.parse_date
"""
from metadate.parse_date import parse_date
from metadate.utils import Units
from dateutil.relativedelta import relativedelta as rd

import sys

__project__ = "metadate"
__version__ = "0.4.63"


def print_version():
    """ Convenient function for printing the version of the package """
    sv = sys.version_info
    py_version = "{}.{}.{}".format(sv.major, sv.minor, sv.micro)
    version_parts = __version__.split(".")
    s = "{} version: [{}], Python {}".format(__project__, __version__, py_version)
    s += "\nMajor version: {}  (breaking changes)".format(version_parts[0])
    s += "\nMinor version: {}  (extra feature)".format(version_parts[1])
    s += "\nMicro version: {} (commit count)".format(version_parts[2])
    return s
