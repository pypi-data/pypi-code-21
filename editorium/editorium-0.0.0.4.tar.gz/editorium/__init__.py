"""
Editorium initialisation.

Note that, we don't import any Qt stuff immediately until default_editorium() is called.
    * to avoid crashing PyQt4 apps 
    * to avoid the seg. fault on Linux 
"""
from editorium.constants import OPTION_ALIGN_LEFT, OPTION_HIDE, OPTION_VISUAL_TRISTATE, OPTION_BOOLEAN_RADIO, OPTION_BOOLEAN_TEXTS
from editorium.defaults import default_editorium, register
