from os import path
from typing import Dict, List, Optional, Tuple, Union, cast

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QTextOption
from PyQt5.QtWidgets import QAction, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog, QLabel, QMenu, QMessageBox, QSizePolicy, QTextEdit, QToolButton, QVBoxLayout, QWidget
from intermake.hosts.frontends.gui_qt.designer.frm_arguments_designer import Ui_Dialog

import editorium
from intermake.engine.environment import MENV
from intermake.engine.function_inspector import NOT_PROVIDED
from intermake.engine.plugin import Plugin
from intermake.engine.plugin_arguments import PluginArg
from mhelper import file_helper, qt_gui_helper, string_helper
from mhelper.qt_gui_helper import AnsiHtmlScheme, exqtSlot


__author__ = "Martin Rusilowicz"

EDITORIUM = editorium.default_editorium()

TDictList = Union[ Dict[ Union[ str, PluginArg ], object ], List[ object ], Tuple[ object ] ]


class Coords:
    def __init__( self, row, col ):
        self.row = row
        self.col = col


class _FrmArguments_Options:
    """
    :data dark_theme: Use the dark theme
    :data grid_mode: Show the arguments in a grid
    :data inline_help: Show help text alongside the arguments, rather than requiring a mouse-over
    """
    def __init__( self ):
        self.dark_theme = False
        self.grid_mode = True
        self.inline_help = False


class FrmArguments( QDialog ):
    SETTINGS_KEY = "gui_arguments"
    
    
    def __init__( self, parent, plugin: Plugin, defaults: TDictList ):
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        self.editors = [ ]
        self.options = MENV.local_data.store.get_and_init( self.SETTINGS_KEY, _FrmArguments_Options() )
        self.main_help_layout = None
        self.__plugin = plugin
        self.__defaults = defaults
        
        self.__init_controls( )
    
    
    def __init_controls( self ):
        if self.options.dark_theme:
            file_main = "arguments_dark.css"
            file_help = "help_box_dark.css"
            lookup = qt_gui_helper.ansi_scheme_dark( bg = "#00000000", fg = "#EFF0F1" )
        else:
            file_main = "arguments_light.css"
            file_help = "help_box_light.css"
            lookup = qt_gui_helper.ansi_scheme_light( bg = "#00000000", fg = "#000000" )
        
        self.css_main = file_helper.read_all_text( path.join( file_helper.get_directory( __file__ ), "designer", file_main ) )
        self.css_help_box = file_helper.read_all_text( path.join( file_helper.get_directory( __file__ ), "designer", file_help ) )
        self.setStyleSheet( self.css_main )
        grid = self.ui.GRID_ARGS
        
        self.__delete_children( grid )
        
        if self.main_help_layout is not None:
            self.main_help_layout.setParent( None )
        
        info = self.__plugin.visualisable_info()
        description = self.__plugin.get_description()
        description = MENV.host.substitute_text( description )
        self.ui.LBL_PLUGIN_NAME.setText( string_helper.capitalise_first_and_fix( info.name ) )
        self.ui.LBL_PLUGIN_ICON.setPixmap( info.icon.icon().pixmap( 32, 32 ) )
        self.main_help_layout = self.create_help_label( description, True, cast( Tuple[ QWidget ], (self.ui.LBL_PLUGIN_NAME, self.ui.LBL_PLUGIN_ICON) ), lookup )
        self.layout().insertLayout( 1, self.main_help_layout )
        coords = Coords( 0, 0 )
        for index, plugin_arg in enumerate(self.__plugin.args):
            if self.options.grid_mode:
                self.__mk_editor_grid( grid, plugin_arg, coords, lookup, index )
            else:
                self.__mk_editor_expanded( grid, plugin_arg, coords, lookup, index )
    
    
    @staticmethod
    def __delete_children( layout ):
        for i in reversed( range( layout.count() ) ):
            layout.itemAt( i ).widget().setParent( None )
    
    
    def __mk_editor_expanded( self, grid: QGridLayout, plugin_arg: PluginArg, coords: Coords, lookup: AnsiHtmlScheme, index:int ):
        parameter_groupbox = QGroupBox()
        parameter_groupbox.setTitle( string_helper.capitalise_first_and_fix( plugin_arg.name ) )
        parameter_groupbox.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Minimum )
        parameter_groupbox.setWhatsThis( plugin_arg.type_description )
        parameter_layout = QVBoxLayout()
        parameter_groupbox.setLayout( parameter_layout )
        
        grid.addWidget( parameter_groupbox, coords.row, coords.col )
        
        coords.row += 1
        if coords.row == 8:
            coords.row = 0
            coords.col += 1
        
        help_layout = self.create_help_label( plugin_arg.get_formatted_description(), True, cast( Tuple[ QWidget ], (parameter_groupbox,) ), lookup )
        parameter_layout.addLayout( help_layout )
        editor = self.__mk_editorium( plugin_arg, index )
        
        parameter_layout.addWidget( editor.editor )
    
    
    def __mk_editorium( self, plugin_arg, index:int ):
        messages = { }
        defaults : TDictList = self.__defaults
        
        messages[ editorium.OPTION_BOOLEAN_RADIO ] = True
        
        if self.options.grid_mode:
            messages[ editorium.OPTION_ALIGN_LEFT ] = True
        
        editor = EDITORIUM.get_editor( plugin_arg.type, messages = messages )
        editor.editor.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Minimum )
        
        if isinstance(defaults, dict) and plugin_arg.name in defaults:
            editor.set_value( defaults[ plugin_arg.name ] )
        elif isinstance(defaults, dict) and plugin_arg in defaults:
            editor.set_value( defaults[ plugin_arg ] )
        elif isinstance(defaults, list) or isinstance(defaults, tuple) and index < len(defaults):
            editor.set_value( defaults[ index ] )
        elif plugin_arg.default is not NOT_PROVIDED:
            editor.set_value( plugin_arg.default )
        
        self.editors.append( (plugin_arg, editor) )
        return editor
    
    
    def __mk_editor_grid( self, grid: QGridLayout, plugin_arg, coords, lookup: AnsiHtmlScheme, index:int ):
        # NAME LABEL
        label = QLabel()
        label.setText( '<a href="." style="color:{}; text-decoration: none">{}</a>'.format( lookup.values[ -1 ][ 1 ], plugin_arg.name ) )
        label.setWhatsThis( plugin_arg.type_description )
        label.linkActivated[ str ].connect( self.help_button_clicked )
        label.setStyleSheet( "QLabel:hover{background:#FFFFE0}" )
        grid.addWidget( label, coords.row, coords.col )
        
        # Input
        editor = self.__mk_editorium( plugin_arg, index )
        grid.addWidget( editor.editor, coords.row, coords.col + 1 )
        self.create_help_label( plugin_arg.get_formatted_description(), False, cast( Tuple[ QWidget ], (label, editor.editor) ), lookup )
        
        coords.row += 1
    
    
    def create_help_label( self, help_text: str, has_parent: bool, relevance: Tuple[ QWidget ], lookup: AnsiHtmlScheme ):
        help_text = help_text.strip()
        help_text_abv = string_helper.max_width( help_text, 120 )
        html = qt_gui_helper.ansi_to_html( help_text, lookup = lookup )
        html_abv = qt_gui_helper.ansi_to_html( help_text_abv, lookup = lookup )
        
        if self.options.inline_help and has_parent:
            help_layout = QHBoxLayout()
            
            help_label = QTextEdit()
            help_label.setStyleSheet( self.css_help_box )
            help_label.setMaximumHeight( 24 )
            help_label.setReadOnly( True )
            help_label.setAcceptRichText( True )
            help_label.setWordWrapMode( QTextOption.NoWrap )
            help_label.setHtml( html_abv )
            help_label.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
            help_label.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
            help_label.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
            help_label.setWhatsThis( html )
            
            help_button = QToolButton()
            help_button.setText( "..." )
            help_button.setSizeIncrement( QSizePolicy.Fixed, QSizePolicy.Fixed )
            help_button.clicked[ bool ].connect( self.help_button_clicked )
            help_button.setToolTip( html )
            help_button.setWhatsThis( html )
            
            help_layout.addWidget( help_label )
            help_layout.addWidget( help_button )
        else:
            help_layout = None
        
        for w in relevance:
            w.setToolTip( html )
            w.setWhatsThis( html )
        
        return help_layout
    
    
    def help_button_clicked( self, _: object ):
        html = self.sender().toolTip()
        QMessageBox.information( self, "Help", html )
    
    
    @staticmethod
    def request( owner_window: QWidget, plugin: Plugin, defaults: Optional[TDictList] = None ) -> None:
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
            form.exec_()
        except Exception as ex:
            from mhelper.print_helper import print_exception
            print_exception( ex )
            raise
    
    
    def __selected_args( self ):
        kw_arg_dict = { }
        
        for plugin_arg, value_fn in self.editors:
            kw_arg_dict[ plugin_arg.name ] = value_fn.get_value()
        
        return kw_arg_dict
    
    
    @exqtSlot( bool )
    def on_BTN_MORE_clicked( self, _: bool ) -> None:
        """
        Signal handler:
        """
        menu = QMenu( self )
        
        toggle_help = menu.addAction( "Inline help" )  # type: QAction
        toggle_help.setCheckable( True )
        toggle_help.setChecked( self.options.inline_help )
        
        toggle_grid = menu.addAction( "Grid view" )  # type: QAction
        toggle_grid.setCheckable( True )
        toggle_grid.setChecked( self.options.grid_mode )
        
        toggle_dark = menu.addAction( "Dark theme" )  # type: QAction
        toggle_dark.setCheckable( True )
        toggle_dark.setChecked( self.options.dark_theme )
        
        menu.addSeparator()
        
        to_command_line = menu.addAction( "To command line" )
        
        selection = menu.exec_( self.ui.BTN_MORE.mapToGlobal( QPoint( 0, self.ui.BTN_MORE.height() ) ) )
        
        if selection is not None:
            if selection == toggle_help:
                self.options.inline_help = not self.options.inline_help
                self.__save_options()
            elif selection == toggle_dark:
                self.options.dark_theme = not self.options.dark_theme
                self.__save_options()
            elif selection == toggle_grid:
                self.options.grid_mode = not self.options.grid_mode
                self.__save_options()
            elif selection == to_command_line:
                s = [ MENV.host.translate_name( self.__plugin.name ) ]
                
                for k, v in self.__selected_args().items():
                    from intermake.hosts.console import ConsoleHost
                    
                    if isinstance( v, list ):
                        s.append( '{}={}'.format( ConsoleHost.translate_name_mode( k, True ), ",".join( str( x ) for x in v ) ) )
                    else:
                        s.append( '{}={}'.format( ConsoleHost.translate_name_mode( k, True ), v ) )
                
                text = " ".join( (x if " " not in x else '"{}"'.format( x )) for x in s )
                
                QInputDialog.getText( self, self.windowTitle(), "Result", text = text )
    
    
    def __save_options( self ):
        MENV.local_data.store[ self.SETTINGS_KEY ] = self.options
        self.__init_controls()
    
    
    @exqtSlot()
    def on_pushButton_clicked( self ) -> None:
        """
        Signal handler:
        """
        try:
            kw_arg_dict = self.__selected_args()
            self.__plugin.run( **kw_arg_dict )
            self.close()
        except Exception as ex:
            qt_gui_helper.show_exception( self, "Error running plugin", ex )
