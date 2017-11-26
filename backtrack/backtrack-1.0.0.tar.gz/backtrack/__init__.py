import sys

if sys.version_info.major < 3:
    raise RuntimeError("Python versions older than 3 are not supported")

from .logger import *
