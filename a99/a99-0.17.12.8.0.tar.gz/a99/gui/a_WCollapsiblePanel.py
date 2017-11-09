__all__ = ["WCollapsiblePanel"]


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99


class WCollapsiblePanel(QWidget):
    """
    Collapsible panel

    Attributes:
       self.widget -- populate this
       self.collapsed_label -- label to become visible when collapsed. Set its text to show some
                               text when collapsed
    """

    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.flag_collapsed = False
        self.button_text_expanded = "^"
        self.button_text_collapsed = "v"


        lh = self.layout = QHBoxLayout(self)
        a99.set_margin(lh, 0)
        lh.setSpacing(2)

        lv = self.layout1 = QVBoxLayout()
        lh.addLayout(lv)
        a99.set_margin(lv, 0)
        lv.setSpacing(0)

        b = self.button = QPushButton("^")
        b.setFixedWidth(16)
        b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        b.clicked.connect(self.collapse_expand_clicked)
        lv.addWidget(b)
        lv.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.widget = QWidget()
        lh.addWidget(self.widget)

        # lh.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        label = self.label = QLabel()
        label.setVisible(False)
        lh.addWidget(label)

    def collapse_expand_clicked(self):
        self.flag_collapsed =  not self.flag_collapsed
        self.widget.setVisible(not self.flag_collapsed)
        self.button.setText(self.button_text_collapsed if self.flag_collapsed else self.button_text_expanded)
        self.label.setVisible(self.flag_collapsed)
