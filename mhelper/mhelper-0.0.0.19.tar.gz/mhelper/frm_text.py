from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from mhelper.designer.frm_text_designer import Ui_Dialog


class FrmText(QDialog):
    def __init__( self, parent, message, text ):
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        self.setWindowTitle(message)
        self.ui.TXT_MAIN.setText(text)
        
    @staticmethod
    def show_text(parent, message, text):
        frm = FrmText(parent, message, text)
        frm.ui.BTNBOX_MAIN.button(QDialogButtonBox.Cancel).setVisible(False)
        
        return frm.exec_()
        
    @pyqtSlot()
    def on_BTNBOX_MAIN_accepted(self) -> None:
        """
        Signal handler:
        """
        self.accept()
    
    @pyqtSlot()
    def on_BTNBOX_MAIN_rejected(self) -> None:
        """
        Signal handler:
        """
        self.reject()
