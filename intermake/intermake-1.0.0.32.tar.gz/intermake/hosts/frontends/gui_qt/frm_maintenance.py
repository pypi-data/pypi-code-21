from typing import cast

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QFrame, QProgressBar, QTextEdit, QWidget, QMenu, QAction
from os import path

from intermake.engine.environment import MENV
from mhelper import qt_gui_helper, file_helper
from intermake.engine.async_result import AsyncResult
from intermake.engine.constants import EDisplay
from intermake.engine.progress_reporter import UpdateInfo
from intermake.hosts.frontends.gui_qt.designer.frm_maintenance_designer import Ui_Dialog
from intermake.hosts.frontends.gui_qt.views.progress_view import ProgressView
from mhelper.qt_gui_helper import exqtSlot


__author__ = "Martin Rusilowicz"

class FrmMaintenance( QDialog ):
    def __init__( self, parent: QWidget, title: str ):
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self)
        
        main = file_helper.read_all_text( path.join( file_helper.get_directory( __file__ ), "designer", "main.css" ) )
        self.setStyleSheet(main)
        
        self.ui.FRA_TITLE.setVisible(False)
        self.ui.SPL_MAIN.setVisible(False)
        
        self.setWindowTitle( title )
        self.setWindowFlags( Qt.Dialog | Qt.Desktop )
        
        self._was_cancelled = False
        from intermake.hosts.gui import GuiHost
        self._auto_close = cast(GuiHost, MENV.host).gui_settings.gui_auto_close_progress
        self._finished = False
        
        self._log_view = ProgressView( self.ui.TVW_LOG, self.ui.BTN_SCROLL )
        self.ui.BTN_SCROLL.setChecked( self._log_view.auto_scroll( ) )
        self.ui.BTN_AUTOCLOSE.setChecked( self._auto_close )
        
        self.ui.TXT_TITLE.setText( title )
        
        self.ui.BTN_SHOW_PROGRESS.setChecked( True )
        self.on_BTN_SHOW_PROGRESS_clicked( )
        
        self.needs_raise = True
        self.__display = EDisplay.TIME_REMAINING
    
    
    def closeEvent( self, event: QCloseEvent ):
        if not self._finished:
            event.ignore( )
    
    
    def was_cancelled( self ):
        return self._was_cancelled
    
    
    def worker_update( self, info: UpdateInfo ):
        if info.message:
            self.__add_message(info.message)
        else:
            self._log_view.add( info )
            bar = self.ui.PRG_BASIC #type: QProgressBar
            
            if info.value > 0 and info.max > 0:
                bar.setValue((info.value * 100) / info.max)
            else:
                bar.setValue(0)
            
            self.ui.TXT_ESTIMATE.setText( info.format_time( self.__display ) )
        
        
        if self.needs_raise:
            self.raise_()
            self.activateWindow()
            self.needs_raise = False
        
    def __add_message(self, m):
        html = qt_gui_helper.ansi_to_html( m )
        self.ui.TXT_MESSAGES.append( html )
    
    
    def worker_finished( self, result: AsyncResult ):
        self._finished = True
        
        # Tag the messages on the result
        txt_box = self.ui.TXT_MESSAGES #type: QTextEdit
        result.ex_messages_html = txt_box.toHtml()  
        
        if self._auto_close:
            self.close( )
        else:
            self._log_view.add_comment( "All done.", "You may now close the dialogue" )
            self.ui.BTN_CANCEL.setEnabled( False )
            self.ui.BTN_AUTOCLOSE.setEnabled( False )
            self.ui.BTN_SCROLL.setEnabled( False )
            self.ui.BTN_CLOSE.setEnabled( True )
    
    
    @exqtSlot( )
    def on_BTN_CANCEL_clicked( self ) -> None:
        """
        Signal handler:
        """
        self._log_view.add_comment( "~~ Cancel requested ~~", "The process will stop during the next iteration" )
        self.ui.BTN_CANCEL.setEnabled( False )
        self._was_cancelled = True
    
    
    @exqtSlot( )
    def on_BTN_AUTOCLOSE_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot( )
    def on_BTN_SCROLL_OUTPUT_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot( )
    def on_BTN_CLOSE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.close( )
        
    @exqtSlot()
    def on_BTN_ESTIMATE_clicked(self) -> None:
        """
        Signal handler:
        """
        menu = QMenu()
        
        options = {}
        
        for option in EDisplay:
            action = menu.addAction(option.name) #type: QAction
            action.setCheckable(True)
            action.setChecked(option == self.__display)
            options[action] = option

        r = menu.exec_( self.ui.BTN_ESTIMATE.mapToGlobal( QPoint( 0, self.ui.BTN_ESTIMATE.height() ) ) )

        if r is not None:
            self.__display = options[r]
        
        
            
    @exqtSlot()
    def on_BTN_DETAILS_clicked(self) -> None:
        """
        Signal handler:
        """
        vis = self.ui.SPL_MAIN.isVisible()
        self.ui.SPL_MAIN.setVisible(not vis)
        self.ui.FRA_BASIC.setVisible(vis)
        self.ui.BTN_DETAILS.setText("Show details" if vis else "Hide details")
            
    @exqtSlot( )
    def on_BTN_SHOW_OUTPUT_clicked( self ) -> None:
        """
        Signal handler:
        """
        child = self.ui.SPL_MAIN.children( )[ 1 ]  # type: QFrame
        child.setVisible( not self.ui.BTN_SHOW_OUTPUT.isChecked( ) )
    
    
    @exqtSlot( )
    def on_BTN_SHOW_PROGRESS_clicked( self ) -> None:
        """
        Signal handler:
        """
        child = self.ui.SPL_MAIN.children( )[ 0 ]  # type: QFrame
        child.setVisible( not self.ui.BTN_SHOW_PROGRESS.isChecked( ) )
    
    
    @exqtSlot( )
    def on_BTN_SCROLL_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot( bool )
    def on_BTN_AUTOCLOSE_toggled( self, checked: bool ) -> None:
        """
        Signal handler:
        """
        self._auto_close = checked
    
    
    @exqtSlot( bool )
    def on_BTN_SCROLL_toggled( self, checked: bool ) -> None:
        """
        Signal handler:
        """
        pass
    