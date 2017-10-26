from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from . import WBase
import os

__all__ = ["WSelectDir", "WSelectFile"]


class _WSelectFileOrDir(WBase):
    @property
    def value(self):
        return self._get_value()

    @value.setter
    def value(self, value):
        self._set_value(value)

    @property
    def flag_valid(self):
        return self._flag_valid

    @flag_valid.setter
    def flag_valid(self, value):
        self._flag_valid = value
        self._update_gui()

    def __init__(self, *args, dialog_title="", dialog_path=".", dialog_wild="*"):
        a99.WBase.__init__(self, *args)

        self._last_value = None
        self._last_exists = None
        # This affects the edit background (red when _flag_valid is false
        self._flag_valid = True

        self._type = None
        self.dialog_title = dialog_title
        self.dialog_path = dialog_path
        self.dialog_wild = dialog_wild

        lw = QHBoxLayout()
        a99.set_margin(lw, 0)
        lw.setSpacing(4)
        self.setLayout(lw)

        # t = self.label = self.keep_ref(QLabel())
        # lw.addWidget(t)

        e = self.edit = QLineEdit()
        e.textEdited.connect(self._on_text_edited)
        lw.addWidget(e)
        # e.setReadOnly(True)

        b = self.button = QToolButton()
        b.clicked.connect(self._on_button_clicked)
        lw.addWidget(b)
        b.setFixedWidth(30)

        # Forces paint red if invalid
        self._on_text_edited()

    def _on_button_clicked(self, _):
        self._act_on_button_clicked()

    def _on_text_edited(self):
        self._act_on_change()

    def _update_gui(self):
        a99.style_widget_valid(self.edit, self._flag_valid)

    def _wanna_emit(self):
        value_now = self._get_value()
        # Maybe it is overzealous to only notify if the last valid filename is not the current one
        if True or value_now != self._last_value:
            self._last_value = value_now
            self.changed.emit()

    def _get_value(self):
        return self.edit.text().strip()

    def _set_value(self, value):
        if value is None:
            value = ""
        self.edit.setText(value)
        self._last_value = value
        self._last_exists = os.path.isfile(value)

    def _act_on_button_clicked(self):
        raise NotImplementedError()

    def _set_text_from_file_dialog(self, text):
        self.edit.setText(text)
        self.dialog_path = text
        self._act_on_change()

    def _act_on_change(self):
        exists = os.path.isfile(self._get_value())
        if not exists and self._last_exists:
            self._last_exists = False
            self.changed.emit()
        elif exists:
            self._last_exists = True
            self._wanna_emit()


class WSelectFile(_WSelectFileOrDir):
    def __init__(self, *args, **kwargs):
        _WSelectFileOrDir.__init__(self, *args, **kwargs)
        # self.label.setText("&File")
        self.button.setIcon(a99.get_icon("document-open"))

    def _on_button_clicked(self):
        path_ = self.edit.text().strip()
        if len(path_) == 0:
            path_ = self.dialog_path
        res = QFileDialog.getOpenFileName(self, self.dialog_title, path_,
                                          self.dialog_wild)[0]
        if res:
            self._set_text_from_file_dialog(res)


class WSelectDir(_WSelectFileOrDir):
    def __init__(self, *args, **kwargs):
        _WSelectFileOrDir.__init__(self, *args, **kwargs)
        self.button.setIcon(a99.get_icon("folder-change"))
        self.edit.setText(self.dialog_path)

    def _act_on_button_clicked(self):
        path_ = self.edit.text().strip()
        if len(path_) == 0:
            path_ = self.dialog_path
        res = QFileDialog.getExistingDirectory(self, self.dialog_title, path_)
        if len(res) > 0:
            self._set_text_from_file_dialog(res)


    def _validate(self):
        return os.path.isdir(self.value)
