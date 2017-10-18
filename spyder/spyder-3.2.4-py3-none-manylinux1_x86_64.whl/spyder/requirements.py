# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""Module checking Spyder installation requirements"""

import sys
import os.path as osp
from distutils.version import LooseVersion


def show_warning(message):
    """Show warning using Tkinter if available"""
    try:
        # If Tkinter is installed (highly probable), showing an error pop-up
        import Tkinter, tkMessageBox
        root = Tkinter.Tk()
        root.withdraw()
        tkMessageBox.showerror("Spyder", message)
    except ImportError:
        pass
    raise RuntimeError(message)

def check_path():
    """Check sys.path: is Spyder properly installed?"""
    dirname = osp.abspath(osp.join(osp.dirname(__file__), osp.pardir))
    if dirname not in sys.path:
        show_warning("Spyder must be installed properly "
                     "(e.g. from source: 'python setup.py install'),\n"
                     "or directory '%s' must be in PYTHONPATH "
                     "environment variable." % dirname)

def check_qt():
    """Check Qt binding requirements"""
    qt_infos = dict(pyqt5=("PyQt5", "5.2"), pyqt=("PyQt4", "4.6"))
    try:
        import qtpy
        package_name, required_ver = qt_infos[qtpy.API]
        actual_ver = qtpy.PYQT_VERSION
        if LooseVersion(actual_ver) < LooseVersion(required_ver):
            show_warning("Please check Spyder installation requirements:\n"
                         "%s %s+ is required (found v%s)."
                         % (package_name, required_ver, actual_ver))
    except ImportError:
        show_warning("Failed to import qtpy.\n"
                     "Please check Spyder installation requirements:\n\n"
                     "qtpy 1.1.0+ and either\n"
                     "%s %s+ or\n"
                     "%s %s+\n\n"
                     "are required to run Spyder."
                     % (qt_infos['pyqt5'] + qt_infos['pyqt']))
