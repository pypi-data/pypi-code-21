from folstools.qt.utils import *


class CaptchaBox(QDialog):
    def __init__(self, img, title='验证码', parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        layout = QVBoxLayout()

        label = QLabel('Captcha Image ................')
        layout.addWidget(label)
        if img:
            pixmap = QPixmap(img)
            label.setPixmap(pixmap)

        self._edit = QLineEdit('')
        layout.addWidget(self._edit)

        ok = QPushButton('OK')
        self.connect(ok, SIGNAL("clicked()"), self._onOK)
        layout.addWidget(ok)

        self.setLayout(layout)

        self.code = ''

    def _onOK(self):
        self.code = self._edit.text()
        return self.accept()


if __name__ == '__main__':
    app = QApplication([])
    app.setOrganizationDomain('fols.com')
    app.setOrganizationName('fols')
    app.setApplicationName('CaptchaBox')
    app.setApplicationVersion('1.0.0')
    dlg = CaptchaBox(None)
    dlg.show()
    app.exec_()
    print(dlg.code)
