from os import path
from typing import Callable, Dict, List, Optional, cast
from warnings import warn

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractButton, QAction, QFrame, QHBoxLayout, QMenu, QSizePolicy, QSpacerItem, QTextEdit, QToolButton, QTreeWidget, QTreeWidgetItem

from intermake.engine import m_print_helper
from intermake.engine.environment import MENV
from intermake.engine.plugin import Plugin
from intermake.engine.plugin_manager import PluginFolder
from intermake.hosts.frontends.gui_qt.designer import resources
from intermake.hosts.frontends.gui_qt.frm_arguments import FrmArguments
from intermake.hosts.frontends.gui_qt.views.tree_view import TreeItemInfo, TreeView
from intermake.visualisables.visualisable import EIterVis, UiInfoProperty
from mhelper import MEnum, exceptToGui, exception_helper, file_helper, override, qt_gui_helper, string_helper
from mhelper.qt_helpers.resource_objects import ResourceIcon


__author__ = "Martin Rusilowicz"


class _ERvOrigin( MEnum ):
    INLINE = 1         #type: _ERvOrigin
    TOOLBAR = 2        #type: _ERvOrigin
    CONTEXT_MENU = 3   #type: _ERvOrigin


class _RvArg:
    def __init__( self, view: "ResultsView", tree_item: Optional[ QTreeWidgetItem ], property: Optional[ UiInfoProperty ], mouse: Optional[ QPoint ], reason: _ERvOrigin ):
        """
        :param view:        Calling view 
        :param tree_item:   Tree item (`None` for visibility queries) 
        :param property:    Property (`None` for visibility queries) 
        :param mouse:       Mouse position (`None` for visibility/enabled queries) 
        :param reason:      Reason for calling 
        """
        self.view = view
        self.tree_item = tree_item
        self.property = property
        self.mouse = mouse
        self.reason = reason


class _RvCmd:
    def __init__( self, text: str, tip: str, icon: ResourceIcon, filter: Callable[ [ _RvArg ], bool ], action: Callable[ [ _RvArg ], None ] ):
        """
        :param text:        Display text 
        :param tip:         Display tooltip 
        :param icon:        Display icon 
        :param filter:      Function to get command visibility 
        :param action:      Function to exact command
        """
        self.text = text
        self.tip = tip
        self.icon = icon
        self.filter = filter
        self.action = action


class ResultsView( TreeView ):
    """
    TREE-LIKE TREEVIEW

    Item data is Tuple[Any, Any]:
        Any: The key (displayed using `str()`)
        Any: Anything handled by TypeHandler

    Viewer for query results, dockets, etc.
    """
    
    # Names of Qt property fields
    __PROPERTY_ITEM = "item"
    __PROPERTY_COMMAND = "command"
    
    # Used as update tag to indicate properties need updating
    _INCLUDE_PROPERTIES = object()
    
    # Style sheet for list
    __STYLE_SHEET = file_helper.read_all_text( path.join( file_helper.get_directory( __file__, 2 ), "designer", "list_button.css" ) )
    
    
    @staticmethod
    def __set_text_to_tvw_comment( text, tvw ):
        data = tvw.selected_data()
        
        if data is None:
            text.setText( "" )
            return
    
    
    def __init__( self, widget: QTreeWidget, text_widget: QTextEdit, toolbar_layout: QHBoxLayout, get_source: Callable[ [ ], UiInfoProperty ], selector = None, acceptability = None ):
        super().__init__( widget )
        
        super().set_columns( "Key", "Value", "Type", "Action", "" )
        super().set_resize_on_expand()
        
        self.__num_results = 0
        self.__source = None
        self.__title = None
        self.__text_widget = text_widget
        self.__get_source = get_source
        self.__selector = selector
        self.__acceptability = acceptability
        self.__toolbar_layout = toolbar_layout
        
        self.__toolbar_mapping = { }
        
        for c in self._get_user_commands( _RvArg( self, None, None, None, _ERvOrigin.TOOLBAR ), spacers = True ):
            if c is None:
                self.__add_to_toolbar_separator( toolbar_layout )
            else:
                self.__add_to_toolbar( c, toolbar_layout )
        
        spacer = QSpacerItem( 1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum )
        toolbar_layout.addSpacerItem( spacer )
        
        self.widget.itemSelectionChanged.connect( self.__on_widget_itemSelectionChanged )
        
        self.widget.setContextMenuPolicy( Qt.CustomContextMenu )
        self.widget.customContextMenuRequested.connect( self.__on_widget_customContextMenuRequested )
        
        self.widget.setStyleSheet( self.__STYLE_SHEET )
        
        self.rebuild()
    
    
    @property
    def selector( self ):
        return self.__selector
    
    
    @staticmethod
    def __add_to_toolbar_separator( toolbar_layout ):
        line = QFrame()
        line.setFixedWidth( 8 )
        line.setFrameShape( QFrame.VLine )
        line.setFrameShadow( QFrame.Sunken )
        toolbar_layout.addWidget( line )
    
    
    def __add_to_toolbar( self, command: _RvCmd, toolbar_layout: QHBoxLayout ):
        button = QToolButton()
        button.setFixedSize( QSize( 48, 48 ) )
        button.setText( command.text )
        button.setToolTip( command.tip )
        button.setIcon( command.icon.icon() )
        button.setIconSize( QSize( 24, 24 ) )
        button.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )
        toolbar_layout.addWidget( button )
        self.__toolbar_mapping[ command ] = button
        button.setProperty( self.__PROPERTY_ITEM, None )
        button.setProperty( self.__PROPERTY_COMMAND, command )
        button.clicked[ bool ].connect( self.__on_button_clicked )
        button.setEnabled( False )
    
    
    @exceptToGui()
    def __on_button_clicked( self, _: bool ):
        sender = self.widget.window().sender()
        assert isinstance( sender, QAbstractButton )
        
        item = sender.property( self.__PROPERTY_ITEM )
        
        if item is None:
            item = self.selected_item()
            
            if item is None:
                return
        
        data = cast( UiInfoProperty, self.item_data( item ) )
        command = sender.property( self.__PROPERTY_COMMAND )
        
        command.action( _RvArg( self, item, data, sender.mapToGlobal( QPoint( 0, sender.height() ) ), _ERvOrigin.TOOLBAR ) )
    
    
    @exceptToGui()
    def __on_widget_customContextMenuRequested( self, pos: QPoint ):
        tree = self.widget  # type: QTreeWidget
        item = tree.itemAt( pos )
        
        if item is None:
            return
        
        data = self.item_data( item )  # type: UiInfoProperty
        
        _results_view_commands[ 0 ].action( _RvArg( self, item, data, tree.mapToGlobal( pos ), _ERvOrigin.CONTEXT_MENU ) )
    
    
    @exceptToGui()
    def __on_widget_itemSelectionChanged( self ):
        tree_item = self.selected_item()
        property = self.selected_data()
        
        if property is None:
            self.__text_widget.setText( "" )
            return
        
        assert isinstance( property, UiInfoProperty )
        
        value = property.get_value()
        visualisable_info = value.visualisable_info()
        
        lookup = qt_gui_helper.ansi_scheme_light()
        
        host = MENV.host
        
        comment_string = qt_gui_helper.ansi_to_html( host.substitute_text( visualisable_info.comment or "" ), lookup = lookup )
        
        if len( visualisable_info.value ) > host.console_width or "\n" in visualisable_info.value:
            lookup2 = lookup.copy()
            lookup2.values[ -1 ] = list(lookup2.values[ -1 ])
            lookup2.values[ -1 ][ 3 ] = "Consolas,monospace"
            value_string = qt_gui_helper.ansi_to_html( visualisable_info.value, lookup = lookup2 )
        else:
            value_string = qt_gui_helper.ansi_to_html( visualisable_info.value, lookup = lookup )
            value_string = "<h3>{}</h3>".format( value_string )
        
        prefix = '<html><body style="' + qt_gui_helper.ansi_scheme_get_style( lookup ) + '">'
        suffix = "</body></html>"
        
        name_string = "<h2>{}</h2>".format( visualisable_info.name )
        
        comment_string = "{}".format( comment_string )
        
        self.__text_widget.setText( "{}{}{}{}{}".format( prefix, name_string, value_string, comment_string, suffix ) )
        
        commands = self._get_user_commands( _RvArg( self, tree_item, property, None, _ERvOrigin.CONTEXT_MENU ) )
        
        for key, button in self.__toolbar_mapping.items():
            assert isinstance( button, QToolButton )
            button.setEnabled( key in commands )
    
    
    def root_object( self ) -> Optional[ object ]:
        return self.__source
    
    
    def title( self ) -> Optional[ str ]:
        return self.__title
    
    
    def rebuild( self, new_source = None ):
        """
        Handles the new set of results
        Note that the listing itself is not retained
        """
        if new_source is not None:
            self.__get_source = new_source
        
        self.clear()
        self.__source = self.__get_source()
        
        exception_helper.assert_type( "self.__source", self.__source, UiInfoProperty )
        
        if self.__source is not None:
            self.add( None, self.__source )
        
        self.resize_columns()
    
    
    @staticmethod
    def __valid_item( parent: UiInfoProperty, child: UiInfoProperty, include_properties: bool ):
        if child is None:
            warn( "«{}» gave a None-valued child from `ui_items`. `ui_items` should only yield IVisualisable objects. Maybe `NamedValue(None, ...)` was meant instead?  This is probably an internal error.".format( parent ), UserWarning )
            return False
        
        if include_properties:
            return True
        
        parent_value = parent.get_value() if parent is not None else None
        
        if isinstance( parent_value, Plugin ):
            return False
        
        child_value = child.get_raw_value()
        
        if isinstance( child_value, PluginFolder ):
            return any( x.is_visible for x in child_value )
        
        if isinstance( child_value, Plugin ):
            return child_value.is_visible
        
        if isinstance( child_value, list ) or isinstance( child_value, tuple ) or isinstance( child_value, dict ):
            if len( child_value ) == 0:
                return False
        
        if child_value is None:
            return False
        
        return True
    
    
    def add( self, parent: Optional[ QTreeWidgetItem ], child: UiInfoProperty ):
        exception_helper.assert_type( "child", child, UiInfoProperty )
        self.add_item( parent, child, loader = self.__requires_children( child ) )
    
    
    def __requires_children( self, data: UiInfoProperty ):
        return any( self.__valid_item( data, child, False ) for child in data.get_value().visualisable_info().iter_children( EIterVis.PROPERTIES | EIterVis.CONTENTS ) )
    
    
    @staticmethod
    def _get_user_commands( args: _RvArg, spacers = False ) -> List[ _RvCmd]:
        r = [ ]
        
        for c in _results_view_commands:
            if c is None:
                if spacers:
                    r.append( c )
            elif c.filter( args ):
                r.append( c )
        
        return r
    
    
    @override
    def virtual_update_item( self, node_info: TreeItemInfo ):
        """
        OVERRIDE
        """
        
        node = node_info.item()  # type: QTreeWidgetItem
        property = node_info.data()  # type: UiInfoProperty
        info = property.get_value().visualisable_info()
        
        # Children
        if node_info.add_children():
            include_properties = node_info.update_tag is self._INCLUDE_PROPERTIES
            
            # Add actual items
            children = [ child for child in info.iter_children( EIterVis.CONTENTS | EIterVis.PROPERTIES ) if self.__valid_item( property, child, include_properties ) ]
            children = sorted( children, key = lambda child: child.key )
            
            for child in children:
                self.add( node, child )
            
            # Columns changed
            self.resize_columns()
        
        if self.__acceptability is not None:
            if self.__acceptability( property ):
                colour = info.qcolour()
                colour_2 = QColor( Qt.black )
            else:
                colour = QColor( Qt.gray )
                colour_2 = QColor( Qt.gray )
        else:
            colour = info.qcolour()
            colour_2 = QColor( Qt.black )
        
        # COLUMN: Key
        column = 0
        key_str = MENV.host.translate_name( property.key )
        key_str_b = MENV.host.translate_name( info.name )
        
        if key_str != key_str_b and key_str_b:
            key_str = "{} ({})".format( key_str, key_str_b )
        
        key_str = string_helper.max_width( key_str, 40 )
        
        node.setText( column, key_str )
        node.setForeground( column, colour_2 )
        
        # COLUMN: Value
        lines = list( m_print_helper.wrap( str( info.value ), 80 ) )
        column += 1
        node.setText( column, lines[ 0 ] if len( lines ) == 1 else (lines[ 0 ] + "…") )
        node.setForeground( column, colour )
        
        # COLUMN: Type
        column += 1
        node.setText( column, str( info.type_name ).lower() )
        node.setForeground( column, colour )
        
        # ICON
        node.setIcon( 0, info.icon.icon() )
        
        # COLUMN: Action
        column += 1
        frame = None
        layout = None
        
        for command in self._get_user_commands( _RvArg( self, node, property, None, _ERvOrigin.INLINE ) ):
            if frame is None:
                frame = QFrame()
                layout = QHBoxLayout()
                frame.setLayout( layout )
                layout.setContentsMargins( 0, 0, 0, 0 )
                self.widget.setItemWidget( node, column, frame )
            
            button = QToolButton()
            layout.addWidget( button )
            button.setText( command.text )
            button.setToolTip( command.tip )
            button.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
            button.setIcon( command.icon.icon() )
            button.setProperty( self.__PROPERTY_ITEM, node )
            button.setProperty( self.__PROPERTY_COMMAND, command )
            button.clicked[ bool ].connect( self.__on_button_clicked )


def __create_results_view_commands():
    def __flt__none( _: _RvArg ):
        return False
    
    
    def __flt__no_inline( args: _RvArg ):
        return args.reason != _ERvOrigin.INLINE
    
    
    def __no_selector_is_plugin( args: _RvArg ):
        if args.tree_item is None:
            return args.view.selector is None
        
        return isinstance( args.property.get_value(), Plugin )
    
    
    def __when_selector( _args: _RvArg ):
        return _args.view.selector is not None
    
    
    def __cmd_refresh( args: _RvArg ):
        args.view.update_item( args.tree_item, True )
        args.tree_item.setExpanded( True )
    
    
    def __cmd_details( args: _RvArg ):
        args.view.update_item( args.tree_item, True, ResultsView._INCLUDE_PROPERTIES )
        args.tree_item.setExpanded( True )
    
    
    def __cmd_run( args: _RvArg ):
        plugin = args.property.get_value()
        assert isinstance( plugin, Plugin )
        FrmArguments.request( args.view.widget.window(), plugin )
    
    
    def __cmd_menu( args: _RvArg ):
        menu = QMenu( args.view.widget.window() )
        
        d = cast( Dict[ QAction, _RvCmd ], { } )
        
        for command in args.view._get_user_commands( args ):
            action_item = menu.addAction( command.text )
            action_item.setToolTip( command.tip )
            action_item.setIcon( command.icon.icon() )
            d[ action_item ] = command
        
        selection = menu.exec_( args.mouse )
        
        if selection is not None:
            try:
                d[ selection ].action( _RvArg( args.view, args.tree_item, args.property, args.mouse, _ERvOrigin.CONTEXT_MENU ) )
            except Exception as ex:
                m_print_helper.print_traceback( ex )
    
    
    def __cmd_select( args: _RvArg ):
        args.view.selector( args.property )
    
    
    return [ _RvCmd( "▼", "Show menu", resources.dropdown, __flt__none, __cmd_menu ),
             _RvCmd( "Refresh", "(Re)expand the item with its current properties. Hide advanced properties.", resources.refresh, __flt__no_inline, __cmd_refresh ),
             _RvCmd( "Details", "(Re)expand the item with its current properties. Include advanced properties.", resources.refreshplus, __flt__no_inline, __cmd_details ),
             None,
             _RvCmd( "Run", "Run the plugin", resources.run, __no_selector_is_plugin, __cmd_run ),
             _RvCmd( "Select", "Choose this item", resources.select, __when_selector, __cmd_select ),
             ]


_results_view_commands = __create_results_view_commands()
