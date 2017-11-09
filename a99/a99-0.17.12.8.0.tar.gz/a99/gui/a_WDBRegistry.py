from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from . import WBase


__all__ = ["WDBRegistry"]


class WDBRegistry(WBase):
    """
    Base class for registry widgets

    Comes with
      - table widget
      - tool bar
      - set of actions
      - signals: id_changed, changed
      - 'id' and 'row' properties
    """

    # Emitted whenever the value of the 'id' property changes
    id_changed = pyqtSignal()

    @property
    def id(self):
        """Molecule id or None"""
        return self._get_id()

    @property
    def row(self):
        """Returns current data row: MyDBRow object, or None"""
        ret = None
        i = self.tableWidget.currentRow()
        if i >= 0:
            ret = self._data[i]
        return ret

    @property
    def f(self):
        """Object representing the file being edited (possibly a DataFile object)"""
        return self._f

    @f.setter
    def f(self, f):
        self._f = f
        self._f_changed()

    def __init__(self, *args):
        WBase.__init__(self, *args)

        # # Internal state
        self._flag_populating = False  # activated when populating table
        self._data = []
        self._last_id = None  # to control emitting id_changed signal
        # FileSQLiteDB instance or None
        self._f = None

        # # GUI design

        # ## Actions
        action = self.action_insert = QAction(a99.get_icon("list-add"), "&Insert...", self)
        action.triggered.connect(self.on_insert)
        action.setShortcut("Ins")

        action = self.action_edit = QAction(a99.get_icon("gtk-edit"), "&Edit...", self)
        action.triggered.connect(self.on_edit)
        action.setShortcut("Enter")

        action = self.action_delete = QAction(a99.get_icon("trash"), "&Delete", self)
        action.setShortcut("Del")
        action.triggered.connect(self.on_delete)

        # ## Visual design

        l = QHBoxLayout(self)
        a99.set_margin(l, 2)
        l.setSpacing(3)

        a = self.tableWidget = QTableWidget()
        a.setSelectionMode(QAbstractItemView.SingleSelection)
        a.setSelectionBehavior(QAbstractItemView.SelectRows)
        a.setEditTriggers(QTableWidget.NoEditTriggers)
        a.setFont(a99.MONO_FONT)
        a.setAlternatingRowColors(True)
        # TODO a.setSortingEnabled(True)
        a.installEventFilter(self)
        a.currentCellChanged.connect(self.on_tableWidget_currentCellChanged)
        a.setContextMenuPolicy(Qt.CustomContextMenu)
        a.customContextMenuRequested.connect(self.on_tableWidget_customContextMenuRequested)
        a.itemDoubleClicked.connect(self.on_tableWidget_doubleClicked)

        l.addWidget(a)

        # Adds actions to toolbar

        tb = QToolBar()
        tb.setOrientation(Qt.Vertical)
        l.addWidget(tb)
        tb.addAction(self.action_insert)
        tb.addAction(self.action_edit)
        tb.addAction(self.action_delete)


    def eventFilter(self, source, event):
        # TODO may have to use this if I insert the widget where there is more than one action with same Ins-Enter-Del short cuts (don't know)
        # if event.type() == QEvent.KeyPress:
        #     if event.key() == Qt.Key_Return:
        #         if source == self.tableWidget:
        #             self.on_edit()
        #             return True
        #             # if event.key() == Qt.Key_Delete:
        #             # ...
        return False


    # # "Abstract" methods (must be overriden)

    def _move_to_first(self):
        """Makes top left cell the current cell, if table is not empty"""
        t = self.tableWidget
        if t.rowCount() > 0:
            t.setCurrentCell(0, 0)

    def _do_on_insert(self):
        """Override this and return True if data was changed"""
        raise NotImplementedError()


    def _do_on_edit(self):
        """Override this and return True if data was changed"""
        raise NotImplementedError()


    def _do_on_delete(self):
        """Override this and return True if data was changed"""
        raise NotImplementedError()


    # # Slots

    def on_insert(self):
        if self._do_on_insert():
            self.changed.emit()

    def on_edit(self):
        if self.row is None:
            return
        if self._do_on_edit():
            self.changed.emit()

    def on_delete(self):
        if not self.row:
            return
        if self._do_on_delete():
            self.changed.emit()

    def on_tableWidget_customContextMenuRequested(self, position):
        menu = QMenu()
        menu.addAction(self.action_insert)
        menu.addAction(self.action_edit)
        menu.addAction(self.action_delete)
        action = menu.exec_(self.tableWidget.mapToGlobal(position))


    def on_tableWidget_doubleClicked(self):
        self.on_edit()


    def on_tableWidget_currentCellChanged(self, currentRow, currentColumn, previousRow,
                                          previousColumn):
        if not self._flag_populating:
            self._wanna_emit_id_changed()


    # # Internal gear

    # TODO work with sorting
    def _find_id(self, id_):
        """Moves to row where formula is (if found, otherwise does nothing)"""
        for i, row in enumerate(self._data):
            if row["id"] == id_:
                t = self.tableWidget
                # idx = t.itemFromIndex()
                t.setCurrentCell(i, 0)
                break

    def _wanna_emit_id_changed(self):
        """Filters intentions to emit the id_changed signal (only does if id really changed)"""
        if self._last_id != self._get_id():
            self._last_id = self._get_id()
            self.id_changed.emit()

    def _get_id(self):
        """Getter because using the id property from within was not working"""
        ret = None
        row = self.row
        if row:
            ret = row["id"]
        return ret


    def _f_changed(self):
        """Override this to react on whenever the value of the 'f' property changes"""