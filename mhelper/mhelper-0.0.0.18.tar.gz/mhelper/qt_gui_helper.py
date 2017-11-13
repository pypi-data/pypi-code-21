import traceback
import functools
from typing import Optional

from mhelper import string_helper, ImplementationError
from mhelper.generics_helper import DECORATOR_FUNCTION, DECORATOR, DECORATED


# NB. No global Qt imports.
#     mhelper must run without QT installed and should ideally defer loading of the QT library until it is actually used.


def exceptToGui() -> DECORATOR_FUNCTION:
    """
    DECORATOR
    
    Same as `exqtSlot` but without the `pyqtSlot` bit.
    """
    
    
    def true_decorator( fn ) -> DECORATOR:
        @functools.wraps( fn )
        def fn_wrapper( *args, **kwargs ) -> DECORATED:
            try:
                return fn( *args, **kwargs )
            except Exception as ex:
                show_exception( args[ 0 ], "Error", ex )


        # noinspection PyTypeChecker
        return fn_wrapper
    
    
    return true_decorator


def exqtSlot( *decorator_args ) -> DECORATOR_FUNCTION:
    """
    DECORATOR
    
    `pyqtSlot` is problematic in that if an exception occurs the application will silently exit.
    This decorator replaces `pyqtSlot` by adding not only the decorator, but a simple error handler. 
    """
    
    
    def true_decorator( fn ) -> DECORATOR:
        from PyQt5.QtCore import pyqtSlot
        return pyqtSlot( *decorator_args )( exceptToGui()( fn ) )
    
    
    return true_decorator


def browse_dir_on_textbox( textbox ) -> bool:
    """
    Opens a file browser, using a textbox to retrieve and store the filename.
    :type textbox: QLineEdit
    """
    owner = textbox.window()
    
    from PyQt5.QtWidgets import QFileDialog
    dir_name = str( QFileDialog.getExistingDirectory( owner, "Select directory", textbox.text(), QFileDialog.DontUseNativeDialog ) )
    
    if not dir_name:
        return False
    
    textbox.setText( dir_name )
    
    return True


def browse_dir( owner, existing = None ):
    from PyQt5.QtWidgets import QFileDialog
    return str( QFileDialog.getExistingDirectory( owner, "Select directory", existing, QFileDialog.DontUseNativeDialog ) )


def browse_open_on_textbox( textbox ) -> bool:
    """
    Opens a file browser, using a textbox to retrieve and store the filename.
    :type textbox: QLineEdit
    """
    from mhelper import file_helper
    
    owner = textbox.window()
    directory = file_helper.get_directory( textbox.text() )
    
    from PyQt5.QtWidgets import QFileDialog
    dir_name = str( QFileDialog.getOpenFileName( owner, "Select file", directory ) )
    
    if not dir_name:
        return False
    
    textbox.setText( dir_name )
    
    return True


def browse_save( parent, filter ):
    from mhelper import file_helper
    
    from PyQt5.QtWidgets import QFileDialog
    file_name, file_filter = QFileDialog.getSaveFileName( parent, "Save", "", filter, options = QFileDialog.DontUseNativeDialog )
    
    if file_name:
        if not file_helper.get_extension( file_name ):
            file_filter = get_extension_from_filter( file_filter )
            
            file_name += file_filter
    
    return file_name or None


def browse_open( parent, filter ):
    from PyQt5.QtWidgets import QFileDialog
    file_name, file_filter = QFileDialog.getOpenFileName( parent, "Open", "", filter, options = QFileDialog.DontUseNativeDialog )
    
    return file_name or None


def get_extension_from_filter( file_filter ):
    """
    Gets the first extension from a filter of the form
    
    Data ( *.txt ) --> .txt
    Data (*.txt) --> .txt
    Data (*.txt, *.csv) --> .txt
    Data (*.txt *.csv) --> .txt
    etc.
    """
    file_filter = file_filter.split( "(", 1 )[ 1 ].strip( " *" )
    
    for x in " ,)":
        if x in file_filter:
            file_filter = file_filter.split( x, 1 )[ 0 ]
    return file_filter


# noinspection PyUnusedLocal
def show_exception( owner, message = None, exception = None, traceback_ = None ) -> None:
    if not traceback_:
        traceback_ = traceback.format_exc()
    
    if isinstance( message, BaseException ):
        exception = message
        message = "Error"
    
    from PyQt5.QtWidgets import QMessageBox
    msg = QMessageBox()
    msg.setIcon( QMessageBox.Critical )
    msg.setText( str( message ) )
    
    if isinstance( exception, BaseException ):
        print( str( exception ) )
        print( traceback_ )
        msg.setInformativeText( str( exception ) )
        msg.setDetailedText( traceback_ )
    
    msg.exec_()


def to_check_state( value ):
    from PyQt5.QtCore import Qt
    if value is None:
        return Qt.PartiallyChecked
    elif value:
        return Qt.Checked
    else:
        return Qt.Unchecked


def from_check_state( value ):
    from PyQt5.QtCore import Qt
    if value == Qt.PartiallyChecked:
        return None
    elif value == Qt.Checked:
        return True
    elif value == Qt.Unchecked:
        return False
    else:
        from mhelper.exception_helper import SwitchError
        raise SwitchError( "from_check_state.value", value )


def move_treeview_items( source, destination, only_selected = True ):
    from PyQt5.QtWidgets import QTreeWidget
    assert isinstance( source, QTreeWidget )
    assert isinstance( destination, QTreeWidget )
    
    if only_selected:
        selected_items = source.selectedItems()
    else:
        selected_items = [ ]
        
        for index in range( source.topLevelItemCount() ):
            selected_items.append( source.topLevelItem( index ) )
    
    for item in selected_items:
        index = source.indexOfTopLevelItem( item )
        source.takeTopLevelItem( index )
        destination.addTopLevelItem( item )


class AnsiHtmlScheme:
    def __init__( self, values ):
        self.values = values
    
    
    def copy( self ):
        return AnsiHtmlScheme( dict( self.values ) )


def ansi_scheme_dark( fg = "#FFFFFF", bg = "#000000" ) -> AnsiHtmlScheme:
    """
    Creates a new ANSI scheme, defaulted to dark values.
    """
    #           code :  back,       fore,       style,      family
    return AnsiHtmlScheme( { 30 : ("", "#000000", "", ""),  # back::black
                             31 : ("", "#FF0000", "", ""),  # back::red
                             32 : ("", "#00FF00", "", ""),  # back::green
                             33 : ("", "#FFFF00", "", ""),  # back::yellow
                             34 : ("", "#0000FF", "", ""),  # back::blue
                             35 : ("", "#FF00FF", "", ""),  # back::magenta
                             36 : ("", "#00FFFF", "", ""),  # back::cyan
                             37 : ("", "#FFFFFF", "", ""),  # back::white
                             39 : ("", "*", "", ""),  # back::reset
                             90 : ("", "#808080", "", ""),  # back::light_black
                             91 : ("", "#FF8080", "", ""),  # back::light_red
                             92 : ("", "#80FF80", "", ""),  # back::light_green
                             93 : ("", "#FFFF80", "", ""),  # back::light_yellow
                             94 : ("", "#8080FF", "", ""),  # back::light_blue
                             95 : ("", "#FF80FF", "", ""),  # back::light_magenta
                             96 : ("", "#80FFFF", "", ""),  # back::light_cyan
                             97 : ("", "#FFFFFF", "", ""),  # back::light_white
                             40 : ("#000000", "", "", ""),  # back::black
                             41 : ("#FF0000", "", "", ""),  # back::red
                             42 : ("#00FF00", "", "", ""),  # back::green
                             43 : ("#FFFF00", "", "", ""),  # back::yellow
                             44 : ("#0000FF", "", "", ""),  # back::blue
                             45 : ("#FF00FF", "", "", ""),  # back::magenta
                             46 : ("#00FFFF", "", "", ""),  # back::cyan
                             47 : ("#FFFFFF", "", "", ""),  # back::white
                             49 : ("*", "", "", ""),  # fore::reset
                             100: ("#808080", "", "", ""),  # back::light_black
                             101: ("#FF8080", "", "", ""),  # back::light_red
                             102: ("#80FF80", "", "", ""),  # back::light_green
                             103: ("#FFFF80", "", "", ""),  # back::light_yellow
                             104: ("#8080FF", "", "", ""),  # back::light_blue
                             105: ("#FF80FF", "", "", ""),  # back::light_magenta
                             106: ("#80FFFF", "", "", ""),  # back::light_cyan
                             107: ("#FFFFFF", "", "", ""),  # back::light_white
                             0  : ("*", "*", "*", ""),  # style::reset_all
                             1  : ("", "", "bold", ""),  # style::bright
                             2  : ("", "", "italic", ""),  # style::dim
                             22 : ("", "", "normal", ""),  # style::normal
                             -1 : (bg, fg, "normal", "sans-serif"),  # special code: defaults
                             -2 : ("", "#00C0FF", "", "monospace"),  # quote start
                             -3 : ("", "*", "", "*"),  # end
                             -4 : ("", "", "", "monospace"),  # table start
                             -5 : ("", "", "", "*"),  # end
                             } )


def ansi_scheme_light( fg = "#000000", bg = "#FFFFFF" ) -> AnsiHtmlScheme:
    """
    Creates a new ANSI scheme, defaulted to light values.
    """
    #           code :  back,       fore,       style,      family
    return AnsiHtmlScheme( { 30 : ("", "#000000", "", ""),  # back::black
                             31 : ("", "#C00000", "", ""),  # back::red
                             32 : ("", "#00C000", "", ""),  # back::green
                             33 : ("", "#C0C000", "", ""),  # back::yellow
                             34 : ("", "#0000C0", "", ""),  # back::blue
                             35 : ("", "#C000C0", "", ""),  # back::magenta
                             36 : ("", "#00C0C0", "", ""),  # back::cyan
                             37 : ("", "#C0C0C0", "", ""),  # back::white
                             39 : ("", "*", "", ""),  # back::reset
                             90 : ("", "#C0C0C0", "", ""),  # back::light_black
                             91 : ("", "#FF0000", "", ""),  # back::light_red
                             92 : ("", "#00FF00", "", ""),  # back::light_green
                             93 : ("", "#FFFF00", "", ""),  # back::light_yellow
                             94 : ("", "#0000FF", "", ""),  # back::light_blue
                             95 : ("", "#FF00FF", "", ""),  # back::light_magenta
                             96 : ("", "#00FFFF", "", ""),  # back::light_cyan
                             97 : ("", "#FFFFFF", "", ""),  # back::light_white
                             40 : ("#000000", "", "", ""),  # back::black
                             41 : ("#C00000", "", "", ""),  # back::red
                             42 : ("#00C000", "", "", ""),  # back::green
                             43 : ("#C0C000", "", "", ""),  # back::yellow
                             44 : ("#0000C0", "", "", ""),  # back::blue
                             45 : ("#C000C0", "", "", ""),  # back::magenta
                             46 : ("#00C0C0", "", "", ""),  # back::cyan
                             47 : ("#C0C0C0", "", "", ""),  # back::white
                             49 : ("*", "", "", ""),  # fore::reset
                             100: ("#C0C0C0", "", "", ""),  # back::light_black
                             101: ("#FF0000", "", "", ""),  # back::light_red
                             102: ("#00FF00", "", "", ""),  # back::light_green
                             103: ("#FFFF00", "", "", ""),  # back::light_yellow
                             104: ("#0000FF", "", "", ""),  # back::light_blue
                             105: ("#FF00FF", "", "", ""),  # back::light_magenta
                             106: ("#00FFFF", "", "", ""),  # back::light_cyan
                             107: ("#FFFFFF", "", "", ""),  # back::light_white
                             0  : ("*", "*", "*", ""),  # style::reset_all
                             1  : ("", "", "bold", ""),  # style::bright
                             2  : ("", "", "italic", ""),  # style::dim
                             22 : ("", "", "normal", ""),  # style::normal
                             -1 : (bg, fg, "normal", "sans-serif"),  # special code: defaults
                             -2 : ("", "#0080C0", "", "Consolas, monospace"),  # quote start
                             -3 : ("", "*", "", "*"),  # end
                             -4 : ("", "", "", "Consolas, monospace"),  # table start
                             -5 : ("", "", "", "*"),  # end
                             } )


def ansi_scheme_get_style( lookup: Optional[ AnsiHtmlScheme ] = None ):
    lookup = lookup or ansi_scheme_dark()
    values = lookup.values[ -1 ]
    return 'background:{}; color:{}; font-style:{}; font-family:{}'.format( values[ 0 ], values[ 1 ], values[ 2 ], values[ 3 ] )


def ansi_to_html( text: Optional[ str ], lookup: Optional[ AnsiHtmlScheme ] = None ) -> str:
    if text is None:
        return ""
    
    from mhelper.string_parser import StringParser
    html = [ ]
    
    lookup = lookup.values if lookup is not None else ansi_scheme_dark().values
    default_style = lookup[ -1 ]
    current_style = list( default_style )
    
    text = string_helper.highlight_quotes( text, "`", "`", "\033[-2m", "\033[-3m" )
    text = string_helper.highlight_quotes( text, "┌", "┘", "\033[-4m", "\033[-5m" )
    text = string_helper.highlight_quotes( text, "«", "»", "\033[-2m", "\033[-3m" )
    
    text = text.replace( "\n* ", "\n• " )
    text = text.replace( "\n", '<br/>' )
    text = text.replace( " ", ' ' )
    
    parser = StringParser( text )
    
    html.append( '<span style="background:{}; color:{}; font-style:{}; font-family:{};">'.format( current_style[ 0 ], current_style[ 1 ], current_style[ 2 ], current_style[ 3 ] ) )
    iterations = 0
    
    while not parser.end():
        iterations += 1
        
        if iterations >= 10000:
            raise ImplementationError( "Possible infinite loop in mhelper.qt_gui_helper.ansi_to_html. Internal error. Possible solutions: Use a shorter string. Check the lookup syntax." )
        
        from colorama.ansi import CSI
        html.append( parser.read_past( CSI ) )
        
        if parser.end():
            break
        
        code = int( parser.read_past( "m" ) )
        new_style = lookup[ code ]
        
        for index in range( len( current_style ) ):
            if new_style[ index ]:
                if new_style[ index ] == "*":
                    current_style[ index ] = default_style[ index ]
                else:
                    current_style[ index ] = new_style[ index ]
        
        html.append( '<span style="background:{}; color:{}; font-style:{}; font-family:{};">'.format( current_style[ 0 ], current_style[ 1 ], current_style[ 2 ], current_style[ 3 ] ) )
    
    html.append( '</span>' )
    
    result = "".join( html )
    
    txx = [ "ANSI", text, "HTML", result ]
    from mhelper import file_helper
    file_helper.write_all_text( "temp-del-me.txt", "\n".join( txx ) )
    
    return result


__author__ = "Martin Rusilowicz"


class QtMutex:
    """
    A `QMutex` wrapped in Python.
    
    This is a `QMutex` and requires QT.
    - It is only for the GUI!
    - - Plugins should *not* use this!
    
    Usage:

        ```
        m = QtMutex()
        
        with m:
           . . .
           
        ```
           
    """
    
    
    # TODO: This shouldn't even live in this folder.
    
    def __init__( self ):
        from PyQt5.QtCore import QMutex
        self._mutex = QMutex()
    
    
    def __enter__( self ):
        self._mutex.lock()
        return self
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        self._mutex.unlock()


def suppress_debugging():
    # Disable PyQT logging to console since we use console for other stuff, plus, it's irritating
    # noinspection PyUnusedLocal
    def __message_handler( msg_type, msg_log_context, msg_string ):
        pass
    
    
    from PyQt5 import QtCore
    QtCore.qInstallMessageHandler( __message_handler )
