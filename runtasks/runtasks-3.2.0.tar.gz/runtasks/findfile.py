
import sys, os
from os.path import dirname, join, exists

MAXDIRS  = 30
# (This is here in case I screw something up.  Better than 100% CPU)

def findfile(filename):
    path = os.getcwd()

    for i in range(MAXDIRS):
        fqn = join(path, filename)

        if exists(fqn):
            return fqn

        parent = dirname(path)
        if parent == path:
            break
        path = parent

    sys.exit('Did not find {!r}'.format(filename))
