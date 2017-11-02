from PyQt4.QtCore import *
from PyQt4.QtGui import *
try:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
except:
    pass
MAIN_WINDOW_GEOMETRY = 'mainWindowGeometry'


def create_group(name):
    def _group(func):
        def __group(*args, **kwargs):
            group = QGroupBox(name)
            group.setLayout(func(*args, **kwargs))
            return group
        return __group
    return _group


def set_icon(dlg, iconfile):
    icon = QIcon()
    icon.addPixmap(QPixmap(iconfile))
    dlg.setWindowIcon(icon)


def save_settings(*settings):
    for key, value in settings:
        QSettings().setValue(key, value)


def load_settings(*settings):
    for key, func in settings:
        value = QSettings().value(key)
        if value:
            func(value)


def settings_set_checked(var):
    def wrapper(val):
        var.setChecked(val == 'true' or val == 'True')
    return wrapper


def createGenericBuddyLayout(self, labeltext, attr, create_widget, shown=True):
    layout = QHBoxLayout()
    label = QLabel(labeltext)
    layout.addWidget(label)
    widget = create_widget()
    setattr(self, attr, widget)
    layout.addWidget(widget)
    if not shown:
        label.setShown(False)
        widget.setShown(False)
    return layout


class AutoCloseMessageBox(QMessageBox):
    def setTimeOut(self, timeout, defaultButton):
        self._button = None
        self._timeout = timeout
        self._defaultButton = self.button(defaultButton)
        self._defaultButtonText = self._defaultButton.text()

    def showEvent(self, event):
        self._timeUp()
        super().showEvent(event)

    def getButton(self):
        if self._button is None:
            self._button = self.clickedButton()
        return self.standardButton(self._button)

    def _timeUp(self):
        if self._timeout == 0:
            self._button = self._defaultButton
            self.close()
            return

        self._defaultButton.setText('{} ({})'.format(self._defaultButtonText,
                                                     self._timeout))
        QTimer().singleShot(1000, self._timeUp)
        self._timeout -= 1
