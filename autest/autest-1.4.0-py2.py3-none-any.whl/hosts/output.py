from __future__ import absolute_import, division, print_function
from builtins import map
import sys

from . import common
import hosts.glb as glb

# these function are the "main" function the user will ideally use in a normal application
# They map the logic to the formatter which will format the message as requested
# and do any remapping required.  The formatter is given a "list" of string data do it can
# correctly combine the finial message via as requested


def WriteMessage(*lst, **kw):
    msg = list(map(str, lst))  # map everything to a string
    glb.formatter.writeMessage(msg, **kw)


def WriteMessagef(sfmt, *lst, **kw):
    msg = common.DelayFormat(sfmt, *lst, **kw)
    glb.formatter.writeMessage(msg, **kw)


def WriteWarning(*lst, **kw):
    msg = list(map(str, lst))  # map everything to a string
    glb.formatter.writeWarning(msg, **kw)


def WriteWarningf(sfmt, *lst, **kw):
    msg = common.DelayFormat(sfmt, *lst, **kw)
    glb.formatter.writeWarning(msg, **kw)


def WriteError(*lst, **kw):
    msg = list(map(str, lst))  # map everything to a string
    glb.formatter.writeError(msg, **kw)


def WriteErrorf(sfmt, *lst, **kw):
    msg = common.DelayFormat(sfmt, *lst, **kw)
    glb.formatter.writeError(msg, **kw)


def WriteDebug(catagory, *lst, **kw):
    catagory = common.make_list(catagory)
    catagory.append("all")
    msg = list(map(str, lst))  # map everything to a string
    glb.formatter.writeDebug(catagory, msg, **kw)


def WriteDebugf(catagory, sfmt, *lst, **kw):
    catagory = common.make_list(catagory)
    catagory.append("all")
    msg = common.DelayFormat(sfmt, *lst, **kw)
    glb.formatter.writeDebug(catagory, msg, **kw)


def WriteVerbose(catagory, *lst, **kw):
    catagory = common.make_list(catagory)
    catagory.append("all")
    msg = list(map(str, lst))  # map everything to a string
    glb.formatter.writeVerbose(catagory, msg, **kw)


def WriteVerbosef(catagory, sfmt, *lst, **kw):
    catagory = common.make_list(catagory)
    catagory.append("all")
    msg = common.DelayFormat(sfmt, *lst, **kw)
    glb.formatter.writeVerbose(catagory, msg, **kw)


def WriteProgress(task, msg=None, progress=None, completed=False):
    glb.formatter.writeProgress(task, msg, progress, completed)


# some utility functions

def getCurrentStack(start_depth=0):
    '''
    start_depth tell us where on the stack to
    start getting data, this way we can pass information
    up the stack where the issue is to the user and hide
    where the error is reported
    '''
    frame = sys._getframe(1+start_depth)
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    routine = frame.f_code.co_name
    return (filename, lineno, routine)
