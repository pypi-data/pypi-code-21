from os import path
from typing import Dict, List, Optional, Tuple, Union, cast
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QTextOption
from PyQt5.QtWidgets import QAction, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMenu, QMessageBox, QSizePolicy, QTextEdit, QVBoxLayout, QWidget, QPushButton, QSpacerItem
import editorium
from mhelper import file_helper, qt_gui_helper, string_helper
from mhelper.qt_gui_helper import AnsiHtmlScheme, exqtSlot
from intermake.hosts.frontends.gui_qt.designer.frm_arguments_designer import Ui_Dialog
from intermake.engine.environment import MENV
from intermake.engine.function_inspector import NOT_PROVIDED
from intermake.engine.plugin import Plugin
from intermake.engine.plugin_arguments import PluginArg


__author__ = "Martin Rusilowicz"
TDictList = Union[Dict[Union[str, PluginArg], object], List[object], Tuple[object]]
_Coords_ = "Coords"


class FrmArguments( QDialog ):
    SETTINGS_KEY = "gui_arguments"
    
    
    def __init__( self, parent, plugin: Plugin, defaults: TDictList ):
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        self.ansi_theme = qt_gui_helper.ansi_scheme_light( bg = "#00000000", fg = "#000000" )
        self.editors = []
        self.options = MENV.local_data.store.get_and_init( self.SETTINGS_KEY, _FrmArguments_Options() )
        self.main_help_widget = None
        self.__plugin = plugin
        self.__defaults = defaults
        self.result = None
        self.__init_controls()
    
    
    def __init_controls( self ):
        if self.options.alternate_theme:
            file_main = "arguments_dark.css"
            file_help = "help_box_dark.css"
        else:
            file_main = "arguments_light.css"
            file_help = "help_box_light.css"
        
        self.css_main = file_helper.read_all_text( path.join( file_helper.get_directory( __file__ ), "designer", file_main ) )
        self.css_help_box = file_helper.read_all_text( path.join( file_helper.get_directory( __file__ ), "designer", file_help ) )
        self.setStyleSheet( self.css_main )
        
        grid: QGridLayout = self.ui.GRID_ARGS
        self.__delete_children( grid )
        self.editors.clear()
        
        if self.main_help_widget is not None:
            self.main_help_widget.setParent( None )
        
        info = self.__plugin.visualisable_info()
        description = self.__plugin.get_description()
        description = MENV.host.substitute_text( description )
        self.ui.LBL_PLUGIN_NAME.setText( string_helper.capitalise_first_and_fix( info.name ) )
        self.ui.LBL_PLUGIN_ICON.setPixmap( info.icon.icon().pixmap( 32, 32 ) )
        self.main_help_widget = self.create_help_label( description, [self.ui.LBL_PLUGIN_NAME, self.ui.LBL_PLUGIN_ICON] )
        self.layout().insertWidget( 1, self.main_help_widget )
        coords = Coords( 0, 0 )
        for index, plugin_arg in enumerate( self.__plugin.args ):
            if not self.options.inline_help:
                self.__mk_editor_grid( grid, plugin_arg, coords, index )
            else:
                self.__mk_editor_expanded( grid, plugin_arg, coords, index )
        
        grid.addItem( QSpacerItem( 1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding ) )
    
    
    @staticmethod
    def __delete_children( layout ):
        for i in reversed( range( layout.count() ) ):
            widget = layout.itemAt( i ).widget()
            
            if widget is not None:
                widget.setParent( None )
    
    
    def __mk_editor_expanded( self, grid: QGridLayout, plugin_arg: PluginArg, coords: _Coords_, index: int ):
        # Groupbox
        parameter_groupbox = QGroupBox()
        parameter_groupbox.setTitle( string_helper.capitalise_first_and_fix( plugin_arg.name ) )
        parameter_groupbox.setMaximumWidth( 768 )
        parameter_groupbox.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Minimum )
        parameter_groupbox.setWhatsThis( str( plugin_arg.annotation ) )
        
        # Layout
        parameter_layout = QVBoxLayout()
        parameter_groupbox.setLayout( parameter_layout )
        
        # Position
        grid.addWidget( parameter_groupbox, coords.row, coords.col )
        
        coords.row += 1
        
        # Help label
        help_widget = self.create_help_label( plugin_arg.get_formatted_description(), [parameter_groupbox] )
        parameter_layout.addWidget( help_widget )
        editor = self.__mk_editorium( plugin_arg, index )
        
        parameter_layout.addWidget( editor.editor )
    
    
    def create_help_label( self, help_text: str, controls ) -> QLabel:
        help_text = help_text.strip()
        
        html = qt_gui_helper.ansi_to_html( help_text, lookup = self.ansi_theme )
        
        html = html.replace( "font-family:sans-serif", "font-family:Times New Roman" )
        
        help_label = QLabel()
        help_label.setStyleSheet( self.css_help_box )
        help_label.setWordWrap( True )
        help_label.setText( html )
        help_label.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )
        help_label.setWhatsThis( html )
        
        for control in controls:
            control.setToolTip( html )
            control.setWhatsThis( html )
        
        return help_label
    
    
    def __mk_editorium( self, plugin_arg, index: int ):
        messages = { }
        defaults: TDictList = self.__defaults
        
        if self.options.inline_help:
            messages[editorium.OPTION_BOOLEAN_RADIO] = True
        else:
            messages[editorium.OPTION_ALIGN_LEFT] = True
        
        editor = editorium.default_editorium().get_editor( plugin_arg.type, messages = messages )
        editor.editor.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Minimum )
        
        if isinstance( defaults, dict ) and plugin_arg.name in defaults:
            editor.set_value( defaults[plugin_arg.name] )
        elif isinstance( defaults, dict ) and plugin_arg in defaults:
            editor.set_value( defaults[plugin_arg] )
        elif isinstance( defaults, list ) or isinstance( defaults, tuple ) and index < len( defaults ):
            editor.set_value( defaults[index] )
        elif plugin_arg.default is not NOT_PROVIDED:
            editor.set_value( plugin_arg.default )
        
        self.editors.append( (plugin_arg, editor) )
        return editor
    
    
    def __mk_editor_grid( self, grid: QGridLayout, plugin_arg, coords: _Coords_, index: int ):
        # NAME LABEL
        label = QLabel()
        label.setText( '<a href="." style="color:{}; text-decoration: none">{}</a>'.format( self.ansi_theme.values[-1][1], plugin_arg.name ) )
        label.setWhatsThis( plugin_arg.type_description )
        label.linkActivated[str].connect( self.help_button_clicked )
        label.setStyleSheet( "QLabel:hover{background:#FFFFE0}" )
        grid.addWidget( label, coords.row, coords.col )
        
        # Input
        editor = self.__mk_editorium( plugin_arg, index )
        grid.addWidget( editor.editor, coords.row, coords.col + 1 )
        self.create_help_label( plugin_arg.get_formatted_description(), [label, editor.editor] )
        
        coords.row += 1
    
    
    def help_button_clicked( self, _: object ):
        html = self.sender().toolTip()
        QMessageBox.information( self, "Help", html )
    
    
    @staticmethod
    def request( owner_window: QWidget, plugin: Plugin, defaults: Optional[TDictList] = None ) -> Optional[Dict[str, object]]:
        """
        Shows the arguments request form.
        
        :param owner_window:    Owning window 
        :param plugin:          Plugin to show arguments for 
        :param defaults:        Optional dictionary or list of default arguments. Dictionaries should be indexed by str (name) or PluginArg.
        """
        try:
            if defaults is None:
                defaults = ()
            
            form = FrmArguments( owner_window, plugin, defaults )
            if form.exec_():
                return form.result
            else:
                return None
        except Exception as ex:
            from mhelper.print_helper import print_exception
            print_exception( ex )
            raise
    
    
    def __selected_args( self ):
        kw_arg_dict = { }
        
        for plugin_arg, value_fn in self.editors:
            try:
                kw_arg_dict[plugin_arg.name] = value_fn.get_value()
            except Exception as ex:
                raise ValueError( "The value of the argument «{}» is invalid: ".format( plugin_arg.name ) + str( ex ) ) from ex
        
        return kw_arg_dict
    
    
    @exqtSlot( bool )
    def on_BTN_MORE_clicked( self, _: bool ) -> None:
        """
        Signal handler:
        """
        menu = QMenu( self )
        
        toggle_help: QAction = menu.addAction( "Inline help" )
        toggle_help.setCheckable( True )
        toggle_help.setChecked( self.options.inline_help )
        
        toggle_dark: QAction = menu.addAction( "Dark theme" )
        toggle_dark.setCheckable( True )
        toggle_dark.setChecked( self.options.alternate_theme )
        
        menu.addSeparator()
        
        to_command_line = menu.addAction( "To command line" )
        
        selection = menu.exec_( self.ui.BTN_MORE.mapToGlobal( QPoint( 0, self.ui.BTN_MORE.height() ) ) )
        
        if selection is not None:
            if selection == toggle_help:
                self.options.inline_help = not self.options.inline_help
                self.__save_options()
            elif selection == toggle_dark:
                self.options.alternate_theme = not self.options.alternate_theme
                self.__save_options()
            elif selection == to_command_line:
                from intermake.hosts.console import ConsoleHost
                
                s = [ConsoleHost.translate_name_mode( self.__plugin.name, True )]
                
                for k, v in self.__selected_args().items():
                    if isinstance( v, list ):
                        s.append( '{}={}'.format( ConsoleHost.translate_name_mode( k, True ), ",".join( str( x ) for x in v ) ) )
                    else:
                        s.append( '{}={}'.format( ConsoleHost.translate_name_mode( k, True ), v ) )
                
                text = " ".join( (x if " " not in x else '"{}"'.format( x )) for x in s )
                
                msg = QMessageBox()
                msg.setText( text )
                msg.setWindowTitle( self.windowTitle() + " - to command line" )
                msg.exec_()
    
    
    def __save_options( self ):
        MENV.local_data.store[self.SETTINGS_KEY] = self.options
        self.__init_controls()
    
    
    @exqtSlot()
    def on_pushButton_clicked( self ) -> None:
        """
        Signal handler:
        """
        try:
            self.result = self.__selected_args()
        except Exception as ex:
            qt_gui_helper.show_exception( self, "Error", ex )
            return
        
        self.accept()


class Coords:
    def __init__( self, row, col ):
        self.row = row
        self.col = col


class _FrmArguments_Options:
    """
    :attr dark_theme:   Use the alternate theme
    :attr inline_help:  Show help text alongside the arguments, rather than requiring a mouse-over
    """
    
    
    def __init__( self ):
        self.alternate_theme = False
        self.inline_help = True
