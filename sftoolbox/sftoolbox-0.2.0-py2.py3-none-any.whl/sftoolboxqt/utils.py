from sftoolboxqt import qtgui
from sftoolboxqt import qtcore
import os
import sys


def open_with_default_program(filepath):
    """open the given filepath with default system software
    """
    if hasattr(qtgui, "QDesktopServices"):
        qtgui.QDesktopServices.openUrl(qtcore.QUrl(filepath))
    elif sys.platform == 'win32':
        os.system("start " + filepath)
    elif sys.platform == 'posix':
        os.system('open "{0}"'.format(filepath))
    elif sys.platform in ['linux', 'linux2']:
        os.system('xdg-open "{0}"'.format(filepath))
