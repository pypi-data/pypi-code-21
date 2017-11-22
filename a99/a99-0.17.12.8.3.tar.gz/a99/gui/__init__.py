"""
API to facilitate building a GUI

  - Reusable and subclassable widgets and windows
  - miscellanea of GUI-related features in `xmisc.py`
  - Python syntax highlighter
  -

File naming conventions:
  a_X*.py : classes descending from QMainWindow or QMainDialog
  a_W*.py : widgets

"""

import a99
import logging

# Tests PyQt5: if fails, 'gui' subpackage will be empty
flag_ok = True
try:
    from PyQt5.QtGui import QFont
except ImportError as e:
    logging.warning("Error importing PyQt5.QtCore: '{}', "
        "a99 GUI resources will not be available".format(a99.str_exc(e)))
    flag_ok = False

if flag_ok:
    # ### Standard font to be used in all GUIs
    MONO_FONT = QFont("not_a_font_name")
    MONO_FONT.setStyleHint(QFont.TypeWriter)

    del QFont

    from . import xmisc
    from . import parameter
    from . import syntax
    # The other modules (a_*) have too ugly names to be imported

    from .xmisc import *
    from .parameter import *
    from .syntax import *
    from .errorcollector import *
    from .a_WBase import *
    from .a_WParametersEditor import *
    from .a_WCollapsiblePanel import *
    from .a_XLogDialog import *
    from .a_XLogMainWindow import *
    from .a_XParametersEditor import *
    from .a_WDBRegistry import *
    from .a_WSelectFileOrDir import *
    from .a_WEditor import *
    from .a_WConfigEditor import *

del a99, flag_ok, logging
