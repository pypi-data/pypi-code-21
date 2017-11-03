from __future__ import absolute_import, division, print_function
import os
import stat


def has_program(program, path=None):
    return where_is(program, path) != None


def where_is(program, path=None):
    # get the path we need to check
    if path is None:
        try:
            path = os.environ['PATH'].split(os.pathsep)
        except KeyError:
            # no path set?
            # well there is nothing to find.
            return None
    try:
        pathext = os.environ['PATHEXT'].split(os.pathsep)
    except KeyError:
        pathext = [""]

    for dir in path:
        f = os.path.join(dir, program)
        if pathext:
            for ext in pathext:
                fext = f + ext
                if os.path.isfile(fext):
                    st = os.stat(fext)
                    if stat.S_IMODE(st[stat.ST_MODE]) & stat.S_IXUSR:
                        return os.path.normpath(fext)

    return None
