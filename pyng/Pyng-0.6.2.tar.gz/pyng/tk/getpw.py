#!/usr/bin/python
"""\
@file   getpw.py
@author Nat Goodspeed
@date   2015-12-11
@brief  getpw() function for console-based Python scripts to prompt user for
        password

        This is for console-based Python scripts because it expects there's no
        existing Tk root window.

        If you need to prompt for more than one password, consider using
        form.display_form() instead of successive calls to this function.

$LicenseInfo:firstyear=2015&license=internal$
Copyright (c) 2015, Linden Research, Inc.
$/LicenseInfo$
"""

import Tkinter, tkSimpleDialog
import os
import __main__                         # for filename of main script
from __init__ import WINDOW_TITLE, BULLET

_root = None

def _getroot():
    global _root
    # only need to initialize once
    if _root is None:
        _root = Tkinter.Tk()
        # Don't show lame empty application window
        _root.withdraw()

def getpw(title="password:"):
    _getroot()
    return tkSimpleDialog.askstring(WINDOW_TITLE, title, show=BULLET)
