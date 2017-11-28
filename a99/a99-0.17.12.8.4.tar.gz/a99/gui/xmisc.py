from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .a_XParametersEditor import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT # as NavigationToolbar2QT
import matplotlib.pyplot as plt
import collections
import a99
from threading import Lock
import time
import os


__all__ = [
    "keep_ref",
    "check_return_space", "show_error", "enc_name_descr", "SignalProxy", "are_you_sure",
    "show_warning", "_window_titles", "style_checkboxes", "VerticalLabel", "show_message",
    "get_matplotlib_layout", "nerdify", "place_center", "get_window_title", "style_widget_changed",
    "get_QApplication", "get_icon", "show_edit_form", "snap_left", "snap_right", "enc_name",
    "place_left_top", "reset_table_widget", "table_info_to_parameters", "format_title0",
    "format_title1", "format_title2", "style_widget_valid", "set_margin",
    "get_frame", "set_checkbox_value"
]

_qrefs = []


def keep_ref(obj):
    """Keeps a reference to Python object representing a C++ Qt object

    **Rationale**: Qt windows may simply disappear when the Python object (e.g., QMainWindow())
                   representing a Qt object runs out of scope (i.e., the program leaves the method
                   that created the Python object). Python deletes the object and the C++ object
                   may be deleted as well. Keeping these objects in a list prevents this
                   from happening.

    **Drawback** will keep reference until the Python program finishes.

    Returns: obj
    """
    global _qrefs
    _qrefs.append(obj)
    return obj


def enc_name_descr(name, descr, color=a99.COLOR_DESCR):
    """Encodes html given name and description."""
    return enc_name(name, color)+"<br>"+descr


def enc_name(name, color=a99.COLOR_DESCR):
    """Encodes html given name."""
    return "<span style=\"color: {0!s}; font-weight: bold\">{1!s}</span>".format(color, name)


def style_checkboxes(widget):
    """
    Iterates over widget children to change checkboxes stylesheet.

    The default rendering of checkboxes does not allow to tell a focused one
    from an unfocused one.
    """

    ww = widget.findChildren(QCheckBox)
    for w in ww:
        w.setStyleSheet("QCheckBox:focus {border: 1px solid #000000;}")


def style_widget_changed(spinbox, flag_changed):
    """(Paints background yellow)/(removes stylesheet)"""
    spinbox.setStyleSheet("QWidget {background-color: #FFFF00}" if flag_changed else "")


def style_widget_valid(spinbox, flag_valid):
    """(Paints background pastel red)/(removes stylesheet)

    Reference: http://www.colorhexa.com/ff6961
    """
    spinbox.setStyleSheet("QWidget {background-color: #FF6961}" if not flag_valid else "")


def check_return_space(event, callable_):
    """Checks if event corresponds to Return/Space being pressed and calls callable_ if so."""
    if event.type() == QEvent.KeyPress:
        if event.key() in [Qt.Key_Return, Qt.Key_Space]:
            callable_()
            return True
    return False


def show_error(s):
  QMessageBox.critical(None, "Error", s)


def show_message(s):
  QMessageBox.information(None, "Information", s)


def show_warning(s):
  QMessageBox.warning(None, "Warning", s)


def are_you_sure(flag_changed, evt, parent=None, title="File has been changed",
                 msg="Are you sure you want to exit?"):
    """
    "Are you sure you want to exit" question dialog.

    If flag_changed, shows question dialog. If answer is not yes, calls evt.ignore()

    Arguments:
      flag_changed
      evt -- QCloseEvent instance
      parent=None -- parent form, used to centralize the question dialog at
      title -- title for question dialog
      msg -- text of question dialog

    Returns True or False. True means: "yes, I want to exit"
    """
    if flag_changed:
        r = QMessageBox.question(parent, title, msg,
             QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
        if r != QMessageBox.Yes:
            evt.ignore()


def reset_table_widget(t, rowCount, colCount):
    """Clears and resizes a table widget."""
    t.reset()
    t.horizontalHeader().reset()
    t.clear()
    t.sortItems(-1)
    t.setRowCount(rowCount)
    t.setColumnCount(colCount)


def show_edit_form(obj, attrs=None, title=""):
    """Shows parameters editor modal form.

    Arguments:
       obj -- object to extract attribute values from, or a dict-like
      attrs -- list of attribute names
    """

    if attrs is None:
        if hasattr(obj, "keys"):
            attrs = list(obj.keys())
        else:
            raise RuntimeError("attrs is None and cannot determine it from obj")

    specs = []
    for name in attrs:
        # Tries as attribute, then as key
        try:
            value = obj.__getattribute__(name)
        except AttributeError:
            value = obj[name]

        if value is None:
            value = ""  # None becomes str
        specs.append((name, {"value": value}))
    form = XParametersEditor(specs=specs, title=title)
    r = form.exec_()
    return r, form


# # Coarse solution for hidden window title
# Qt does not account for the window frame.This is being coarsely
# accounted for by setting the position coordinates to values slightly greater
# than 0.
_DESKTOP_OFFSET_LEFT = 2
_DESKTOP_OFFSET_TOP = 15


def place_left_top(window, width=None, height=None):
    """Places window in top left corner of screen.

    Arguments:
      window -- a QWidget
      width=None -- window width, in case you want to change it (if not passed, not changed)
      height=None -- window height, in case you want to change it (if not passed, not changed)
    """

    if width is None:
        width = window.width()
    if height is None:
        height = window.height()

    window.setGeometry(_DESKTOP_OFFSET_LEFT, _DESKTOP_OFFSET_TOP, width, height)


def place_center(window, width=None, height=None):
    """Places window in the center of the screen."""
    screenGeometry = QApplication.desktop().screenGeometry()

    w, h = window.width(), window.height()

    if width is not None or height is not None:
        w = width if width is not None else w
        h = height if height is not None else h
        window.setGeometry(0, 0, w, h)

    x = (screenGeometry.width() - w) / 2
    y = (screenGeometry.height() - h) / 2
    window.move(x, y)


def snap_left(window, width=None):
    """Snaps window to left of desktop.
    Arguments:
      window -- a QWidget
      width=None -- window width, in case you want to change it (if not passed, not changed)
    """
    if not width:
        width = window.width()
    rect = QApplication.desktop().screenGeometry()
    window.setGeometry(_DESKTOP_OFFSET_LEFT, _DESKTOP_OFFSET_TOP, width, rect.height())


def snap_right(window, width=None):
    """Snaps window to right of desktop.
    Arguments:
      window -- a QWidget
      width=None -- window width, in case you want to change it (if not passed, not changed)
    """
    if not width:
        width = window.width()
    rect = QApplication.desktop().screenGeometry()
    window.setGeometry(rect.width()-width, _DESKTOP_OFFSET_TOP, width, rect.height())


def nerdify(window):
    window.setFont(a99.MONO_FONT)


class VerticalLabel(QLabel):
    """Label that draws itself vertically.

    This was created to be used at lateral title:
      - It paints in bold
      - No HTML support
    """
    
    def paintEvent(self, evt):
        painter = QPainter(self)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.Dense1Pattern)
        painter.rotate(90)
        painter.font().setWeight(QFont.Bold)

        # td = QTextDocument()
        # td.setHtml(self.text())
        # td.drawContents(painter)

        painter.drawText(0,0, self.text())

    def minimumSizeHint(self):
        s = QLabel.minimumSizeHint(self)
        return QSize(s.height(), s.width())

    def sizeHint(self):
        s = QLabel.sizeHint()
        return QSize(s.height(), s.width())


def get_matplotlib_layout(widget, flag_toolbar=True):
    """
    Creates figure, toolbar, layout, sets widget layout

    Returns figure, canvas, layout

    Reference: http://stackoverflow.com/questions/12459811

    """
    fig = plt.figure()
    canvas = FigureCanvas(fig)
    #        self.canvas.mpl_connect('button_press_event', self.on_plot_click)
    layout = QVBoxLayout(widget)
    if flag_toolbar:
        toolbar = NavigationToolbar2QT(canvas, widget)
        layout.addWidget(toolbar)
    layout.addWidget(canvas)
    a99.set_margin(layout, 0)

    return fig, canvas, layout


def get_icon(keyword):
    """
    Transforms a PNG file in a QIcon

    Looks for a file named <keyword>.png in the "icons" directory

    If file does not exist, returns None
    """

    filename = a99.get_path( "icons", keyword + ".png")
    if not os.path.isfile(filename):
        raise FileNotFoundError("File '{}' does not exist".format(filename))
    return QIcon(filename)


# Because several windows of the same class may be created, we'll give them different titles to help avoid confusion
_window_titles = collections.Counter()
def get_window_title(prefix):
    _window_titles[prefix] += 1
    i = _window_titles[prefix]
    if i == 1:
        return prefix
    else:
        return "{0!s} #{1:d}".format(prefix, i)


_qapp = None
def get_QApplication(args=[]):
    """Returns the QApplication instance, creating it is does not yet exist."""
    global _qapp
    if _qapp is None:
        QCoreApplication.setAttribute(Qt.AA_X11InitThreads)
        _qapp = QApplication(args)

    return _qapp


class _ThreadsafeTimer(QObject):
    """
    Thread-safe replacement for QTimer.

    Original author: Luke Campagnola -- pyqtgraph package
    """

    timeout = pyqtSignal()
    sigTimerStopRequested = pyqtSignal()
    sigTimerStartRequested = pyqtSignal(object)

    def __init__(self):
        QObject.__init__(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerFinished)
        self.timer.moveToThread(QCoreApplication.instance().thread())
        self.moveToThread(QCoreApplication.instance().thread())
        self.sigTimerStopRequested.connect(self.stop, Qt.QueuedConnection)
        self.sigTimerStartRequested.connect(self.start, Qt.QueuedConnection)


    def start(self, timeout):
        isGuiThread = QThread.currentThread() == QCoreApplication.instance().thread()
        if isGuiThread:
            #print "start timer", self, "from xgear thread"
            self.timer.start(timeout)
        else:
            #print "start timer", self, "from remote thread"
            self.sigTimerStartRequested.emit(timeout)

    def stop(self):
        isGuiThread = QThread.currentThread() == QCoreApplication.instance().thread()
        if isGuiThread:
            #print "stop timer", self, "from xgear thread"
            self.timer.stop()
        else:
            #print "stop timer", self, "from remote thread"
            self.sigTimerStopRequested.emit()

    def timerFinished(self):
        self.timeout.emit()


class SignalProxy(QObject):
    """Object which collects rapid-fire signals and condenses them
    into a single signal or a rate-limited stream of signals.
    Used, for example, to prevent a SpinBox from generating multiple
    signals when the mouse wheel is rolled over it.

    Emits sigDelayed after input signals have stopped for a certain period of time.

    Note: *queued* connection is made to slot.

    Original author: Luke Campagnola -- pyqtgraph package

    Arguments:
      signals -- a list of bound signals or pyqtSignal instance
      delay=0.3 -- Time (in seconds) to wait for signals to stop before emitting
      slot -- Optional function to connect sigDelayed to.
      rateLimit=0 -- (signals/second) if greater than 0, this allows signals to
       stream out at a steady rate while they are being received.
      flag_connect=True -- whether or not to start with the connections already
       made. If False, the signals and slots can be connected by calling
       connect_all()
    """

    __sigDelayed = pyqtSignal(object)

    def __init__(self, signals, delay=0.3, rateLimit=0, slot=None,
                 flag_connect=True):
        QObject.__init__(self)
        # for signal in signals:
        #     self.__connect_signal(signal)
        self.__signals = signals
        self.__delay = delay
        self.__rateLimit = rateLimit
        self.__args = None
        self.__timer = _ThreadsafeTimer()
        self.__timer.timeout.connect(self.__flush)
        self.__disconnecting = False
        self.__slot = slot
        self.__lastFlushTime = None
        self.__lock = Lock()
        # State: connected/disconnected
        self.__connected = False
        if flag_connect:
            self.connect_all()
        # if slot is not None:
        #     self.__sigDelayed.connect(slot, Qt.QueuedConnection)

    def add_signal(self, signal):
        """Adds "input" signal to connected signals.
        Internally connects the signal to a control slot."""
        self.__signals.append(signal)
        if self.__connected:
            # Connects signal if the current state is "connected"
            self.__connect_signal(signal)

    def connect_all(self):
        """[Re-]connects all signals and slots.

        If already in "connected" state, ignores the call.
        """
        if self.__connected:
            return  # assert not self.__connected, "connect_all() already in \"connected\" state"
        with self.__lock:
            for signal in self.__signals:
                self.__connect_signal(signal)
            if self.__slot is not None:
                self.__sigDelayed.connect(self.__slot, Qt.QueuedConnection)
            self.__connected = True

    def disconnect_all(self):
        """Disconnects all signals and slots.

        If already in "disconnected" state, ignores the call.
        """
        if not self.__connected:
            return  # assert self.__connected, "disconnect_all() already in \"disconnected\" state"
        self.__disconnecting = True
        try:
            for signal in self.__signals:
                signal.disconnect(self.__signalReceived)
            if self.__slot is not None:
                self.__sigDelayed.disconnect(self.__slot)
            self.__connected = False
        finally:
            self.__disconnecting = False

    def __signalReceived(self, *args):
        """Received signal. Cancel previous timer and store args to be forwarded later."""
        if self.__disconnecting:
            return
        with self.__lock:
            self.__args = args
            if self.__rateLimit == 0:
                self.__timer.stop()
                self.__timer.start((self.__delay * 1000) + 1)
            else:
                now = time.time()
                if self.__lastFlushTime is None:
                    leakTime = 0
                else:
                    lastFlush = self.__lastFlushTime
                    leakTime = max(0, (lastFlush + (1.0 / self.__rateLimit)) - now)

                self.__timer.stop()
                # Note: original was min() below.
                timeout = (max(leakTime, self.__delay) * 1000) + 1
                self.__timer.start(timeout)

    def __flush(self):
        """If there is a signal queued up, send it now."""
        if self.__args is None or self.__disconnecting:
            return False
        #self.emit(self.signal, *self.args)
        self.__sigDelayed.emit(self.__args)
        self.__args = None
        self.__timer.stop()
        self.__lastFlushTime = time.time()
        return True

    def __connect_signal(self, signal):
        signal.connect(self.__signalReceived, Qt.QueuedConnection)


def table_info_to_parameters(table_info):
    """
    Converts a list of MyDBRow into a parameters.Parameters object

    This facilitates transfering data from SQLite table row to a XParameterEditor window

    See also: get_table_info()
    """

    # Example of item in table_info:
    #   MyDBRow([('cid', 0), ('name', 'id'), ('type', 'integer'), ('notnull', 0), ('dflt_value', None), ('pk', 1)])

    opbj = a99.Parameters()
    for field_info in table_info.values():
        p = a99.Parameter()
        if field_info.type == "integer":
            p.type = int
        elif field_info.type == "real":
            p.type = float
        else:
            p.type = str

        p.name = field_info.name
        if field_info.dflt_value is not None:
            p.value = field_info.dflt_value
        opbj.params.append(p)
    return opbj


def format_title0(s):
    """Formats string as first-level title (to use as QLabel text)"""
    return "<h3>{}</h3>".format(s)


def format_title1(s):
    """Formats string as second-level title (to use as QLabel text)"""
    return "<h4>{}</h4>".format(s)


def format_title2(s):
    """Formats string as third-level title (to use as QLabel text)"""
    return "<h5>{}</h5>".format(s)


def set_margin(obj, margin):
    """...because Qt5 no longer has xxxx.setMargin() method"""
    obj.setContentsMargins(margin, margin, margin, margin)


def get_frame():
    """Returns a QFrame formatted in a particular way"""
    ret = QFrame()
    ret.setLineWidth(1)
    ret.setMidLineWidth(0)
    ret.setFrameShadow(QFrame.Sunken)
    ret.setFrameShape(QFrame.Box)
    return ret

def set_checkbox_value(w, value):
    """
    Sets a checkbox's "checked" property + signal blocking + value tolerance

    Args:
        w: QCheckBox instance
        value: something that can be converted to a bool
    """
    save = w.blockSignals(True)
    try:
        w.setChecked(bool(value))
    finally:
        w.blockSignals(save)

