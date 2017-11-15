from PyQt5.QtWidgets import QDialog
from ._logpart import *

__all__ = ["XLogDialog"]

class XLogDialog(QDialog, _LogPart):
    """QDialog subclass that carries a logging facility"""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        _LogPart.__init__(self)
        self._refs = []