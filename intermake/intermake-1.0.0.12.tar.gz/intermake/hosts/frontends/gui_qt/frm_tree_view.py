from typing import Optional

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from os import path

from intermake.engine.environment import MENV
from intermake.hosts.frontends.gui_qt.designer.frm_tree_view_designer import Ui_Dialog
from intermake.hosts.frontends.gui_qt.views.results_view import ResultsView
from intermake.visualisables.visualisable_operations import PathToVisualisable
from mhelper import file_helper


class FrmTreeView( QDialog ):
    def __init__( self, parent, message, root, acceptability ):
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog(self)
        
        main = file_helper.read_all_text( path.join( file_helper.get_directory( __file__ ), "designer", "main.css" ) )
        self.setStyleSheet(main)
        
        self.ui.LBL_MAIN.setText(str(message))
        self.__results = ResultsView(self.ui.TVW_MAIN, self.ui.TXT_MAIN, self.ui.HOZ_TOOLBAR, lambda : root, self.on_BTNBOX_MAIN_accepted, acceptability)
        self.__acceptability = acceptability
        self._result = None
        self.on_TVW_MAIN_itemSelectionChanged()
        
    @staticmethod
    def request(parent, message, root, acceptability) -> Optional[PathToVisualisable]:
        if root is None:
            root = MENV.root
            
        if message is None:
            message = "Select object"
        
        frm = FrmTreeView(parent,message,root,acceptability)
        
        if frm.exec_():
            return PathToVisualisable(frm._result)
            
        return None        
        
    @pyqtSlot()
    def on_TVW_MAIN_itemSelectionChanged(self) -> None:
        data = self.__results.selected_data()
        
        box = self.ui.BTNBOX_MAIN #type: QDialogButtonBox
        
        if data is not None:
            box.button(QDialogButtonBox.Ok).setEnabled(self.__acceptability(data))
        else:
            box.button(QDialogButtonBox.Ok).setEnabled(False)
        
        
    @pyqtSlot()
    def on_BTNBOX_MAIN_accepted(self) -> None:
        """
        Signal handler:
        """
        path = self.__results.data_path( self.__results.selected_item() )
        
        if path is not None and self.__acceptability(path[-1]):
            self._result = path
            self.accept()
        
    @pyqtSlot()
    def on_BTNBOX_MAIN_rejected(self) -> None:
        """
        Signal handler:
        """
        self.reject()
        