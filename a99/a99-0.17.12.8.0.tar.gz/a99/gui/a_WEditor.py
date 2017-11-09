from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .a_XLogDialog import XLogDialog
from .a_XLogMainWindow import XLogMainWindow
from .a_WBase import *
from . import xmisc
from .. import loggingaux
import os

# Margin for main layout
EDITOR_LAYMN_MAIN = 9
# Spacing for main layout
EDITOR_LAYSP_MAIN = 9

__all__ = ["WEditor", "EDITOR_LAYMN_MAIN", "EDITOR_LAYSP_MAIN"]


class WEditor(WBase):
    """Base class for editor widgets"""

    @property
    def f(self):
        # DataFile instance
        return self._f

    @property
    def flag_valid(self):
        return self._flag_valid

    # Emitted by load()
    loaded = pyqtSignal()

    def __init__(self, *args, **kwargs):
        WBase.__init__(self, *args, **kwargs)

        # Datafile instance
        self._f = None
        # whether file can be saved or not. Handling this is almost completely left to descenadnt
        self._flag_valid = False

        self.setEnabled(False)

        # # Central layout
        l = self.layout_editor = QVBoxLayout()
        xmisc.set_margin(l, EDITOR_LAYMN_MAIN)
        l.setSpacing(EDITOR_LAYSP_MAIN)
        self.setLayout(l)


        ll = self.layout_label_fn = QHBoxLayout()
        l.addLayout(ll)
        xmisc.set_margin(ll, 0)
        ll.setSpacing(3)

        la = self.label_caption_fn = QLabel("<b>File: </b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        ll.addWidget(la)

        la = self.label_fn = QLabel()  # Label that shows the filename
        la.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        ll.addWidget(la)

        ll.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def load(self, fobj):
        flag_ok = False
        try:
            self._do_load(fobj)

            # We trust subclass on this
            self._flag_valid = True

            self.update_gui_label_fn()
            self.setEnabled(True)
            flag_ok = True
        except Exception as E:
            loggingaux.get_python_logger().exception("Loading obj of class '{}'".format(fobj.__class__.__name__))
            xmisc.show_error(loggingaux.str_exc(E))
            self._flag_valid = False
            self._f = None

            # **Note** there is one issue: if fails here, it may leave the GUI partially updated

        if flag_ok:
            self.loaded.emit()

    def update_gui_label_fn(self):
        if hasattr(self, "label_fn"):
            self.label_fn.setText(self._make_fn_text())

    def _make_fn_text(self):
        """Makes filename text"""
        if not self._f:
            text = "(not loaded)"
        elif self._f.filename:
            text = os.path.relpath(self._f.filename, ".")
        else:
            text = "(filename not set)"
        return text

    def _do_load(self, fobj):
        raise NotImplementedError("Please implement {}._do_load()".format(self.__class__.__name__))