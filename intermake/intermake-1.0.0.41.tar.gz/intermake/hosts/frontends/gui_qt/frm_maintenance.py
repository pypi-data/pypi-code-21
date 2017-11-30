from typing import cast

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QWidget, QMenu, QAction
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
    """
    This is the form that shows when a plugin is running.
    """
    
    
    def __init__( self, parent: QWidget, title: str ):
        """
        CONSTRUCTOR
        """
        from intermake.hosts.gui import GuiHost
        
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        
        # Set the style sheet
        main = file_helper.read_all_text( path.join( file_helper.get_directory( __file__ ), "designer", "main.css" ) )
        self.setStyleSheet( main )
        
        # Set our properties
        self.__was_cancelled = False
        self.__auto_close = cast( GuiHost, MENV.host ).gui_settings.gui_auto_close_progress
        self.__finished = False
        self.__log_view = ProgressView( self.ui.TVW_LOG, self.ui.BTN_SCROLL )
        self.__display = EDisplay.TIME_REMAINING
        self.__needs_raise = True
        self.__show_details = False
        self.__maximise_progress = False
        self.__maximise_output = False
        self.__has_text_messages = False
        
        # Set the default view to the simple one
        self.setWindowTitle( title )
        self.setWindowFlags( Qt.Dialog | Qt.Desktop )
        self.ui.FRA_TITLE.setVisible( False )
        self.ui.BTN_SCROLL.setChecked( self.__log_view.auto_scroll() )
        self.__update_auto_close()
        self.__update_show_details()
        self.ui.TXT_TITLE.setText( title )
        self.ui.BTN_SHOW_PROGRESS.setChecked( True )
        self.on_BTN_SHOW_PROGRESS_clicked()
        self.ui.BTN_CLOSE.setVisible( False )
    
    
    def __update_auto_close( self ):
        self.ui.BTN_AUTOCLOSE.setChecked( self.__auto_close )
    
    
    def __update_show_details( self ):
        self.ui.BTN_SHOW_OUTPUT.setChecked( self.__maximise_output )
        self.ui.BTN_SHOW_PROGRESS.setChecked( self.__maximise_progress )
        self.ui.FRA_TITLE.setVisible( not self.__show_details or (not self.__maximise_output and not self.__maximise_progress) )
        self.ui.FRA_PROGRESS.setVisible( not self.__maximise_output )
        self.ui.FRA_MESSAGES.setVisible( not self.__maximise_progress )
        self.ui.SPL_MAIN.setVisible( self.__show_details )
        self.ui.FRA_BASIC.setVisible( not self.__show_details )
        self.ui.BTN_DETAILS.setText( "Hide details" if self.__show_details else "Show details" )
    
    
    # region ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ EXTERNAL COMMANDS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    
    def worker_update( self, info: UpdateInfo ):
        if info.message:
            self.__add_message_to_textbox( info.message )
        else:
            self.__add_progress_to_progress_list( info )
        
        if self.__needs_raise:
            self.activateWindow()
            self.raise_()
            self.__needs_raise = False
    
    
    def was_cancelled( self ) -> bool:
        return self.__was_cancelled
    
    
    def worker_finished( self, result: AsyncResult ):
        self.__finished = True
        
        # Tag the messages onto the result
        result.ex_messages_html = self.ui.TXT_MESSAGES.toHtml()
        
        if self.__auto_close:
            self.close()
        else:
            self.ui.LBL_PLEASE_WAIT.setText( "All done. You may now close the dialogue." )
            self.__log_view.add_comment( "All done.", "You may now close the dialogue" )
            self.ui.BTN_CANCEL.setVisible( False )
            self.ui.BTN_AUTOCLOSE.setVisible( False )
            self.ui.BTN_SCROLL.setVisible( False )
            self.ui.BTN_SCROLL_OUTPUT.setVisible( False )
            self.ui.BTN_CLOSE.setVisible( True )
    
    
    # endregion
    
    
    
    def __add_progress_to_progress_list( self, info ):
        """
        Adds a progress message to the progress list.
        """
        self.__log_view.add( info )
        
        if info.value > 0 and info.max > 0:
            self.ui.PRG_BASIC.setValue( (info.value * 100) / info.max )
        else:
            self.ui.PRG_BASIC.setValue( 0 )
        
        self.ui.TXT_ESTIMATE.setText( info.format_time( self.__display ) )
    
    
    def __add_message_to_textbox( self, message_text ):
        """
        Adds a message to the textbox.
        """
        if not self.__has_text_messages:
            self.__has_text_messages = True
            self.__show_details = True
            self.__maximise_progress = False
            self.__maximise_output = True
            self.__auto_close = False
            self.__update_show_details()
            self.__update_auto_close()
        
        html = qt_gui_helper.ansi_to_html( message_text )
        self.ui.TXT_MESSAGES.append( html )
    
    
    def closeEvent( self, event: QCloseEvent ):
        if not self.__finished:
            event.ignore()
    
    
    @exqtSlot()
    def on_BTN_CANCEL_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.__log_view.add_comment( "~~ Cancel requested ~~", "The process will stop during the next iteration" )
        self.ui.BTN_CANCEL.setVisible( False )
        self.__was_cancelled = True
    
    
    @exqtSlot()
    def on_BTN_AUTOCLOSE_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_SCROLL_OUTPUT_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_CLOSE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.close()
    
    
    @exqtSlot()
    def on_BTN_ESTIMATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        menu = QMenu()
        
        options = { }
        
        for option in EDisplay:
            action: QAction = menu.addAction( option.name )
            action.setCheckable( True )
            action.setChecked( option == self.__display )
            options[action] = option
        
        r = menu.exec_( self.ui.BTN_ESTIMATE.mapToGlobal( QPoint( 0, self.ui.BTN_ESTIMATE.height() ) ) )
        
        if r is not None:
            self.__display = options[r]
    
    
    @exqtSlot()
    def on_BTN_DETAILS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.__show_details = not self.__show_details
        self.__update_show_details()
    
    
    @exqtSlot()
    def on_BTN_SHOW_OUTPUT_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.__maximise_output = self.ui.BTN_SHOW_OUTPUT.isChecked()
        self.__update_show_details()
    
    
    @exqtSlot()
    def on_BTN_SHOW_PROGRESS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.__maximise_progress = self.ui.BTN_SHOW_PROGRESS.isChecked()
        self.__update_show_details()
    
    
    @exqtSlot()
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
        self.__auto_close = checked
    
    
    @exqtSlot( bool )
    def on_BTN_SCROLL_toggled( self, checked: bool ) -> None:
        """
        Signal handler:
        """
        pass
