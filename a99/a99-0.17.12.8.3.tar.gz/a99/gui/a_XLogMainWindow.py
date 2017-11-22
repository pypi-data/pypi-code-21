from PyQt5.QtWidgets import QMainWindow
from ._logpart import *

__all__ = ["XLogMainWindow"]

class XLogMainWindow(QMainWindow, _LogPart):
    """QMainWindow subclass that carries a logging facility"""
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        _LogPart.__init__(self)
        self._refs = []