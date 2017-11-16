"""py version compatibility."""

import sys


VER = sys.version_info
PY2 = VER.major < 3

if PY2:
    from future import print_function
    print = print_function
