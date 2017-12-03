from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QCommonStyle


class Icon(object):
    def __init__(self):
        style = QCommonStyle()
        icons = [x for x in dir(QStyle) if x.startswith('SP_')]
        self.names = []
        for name in icons:
            icon = style.standardIcon(getattr(QStyle, name))
            setattr(self, name[3:], icon)
            self.names.append(name[3:])
