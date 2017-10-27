from typing import List, Optional, Iterator, cast

from PyQt5.QtWidgets import QAbstractButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtWidgets import QTreeWidgetItem

from intermake.visualisables.visualisable import UiInfoProperty
from mhelper import print_helper
from mhelper.comment_helper import abstract
from mhelper.qt_gui_helper import exceptToGui


__author__ = "Martin Rusilowicz"


class TreeItemInfo:
    def __init__( self, item: QTreeWidgetItem, data: object, first: bool, update_tag : Optional[object] ):
        self.__item = item
        self.__data = data
        self.__add_children = first
        self.update_tag = update_tag
    
    
    def item( self ) -> QTreeWidgetItem:
        """
        Item
        """
        return self.__item
    
    
    def data( self ) -> object:
        """
        Associated data
        """
        return self.__data
    
    
    def add_children( self ) -> bool:
        """
        Indicates if children should be added
        """
        return self.__add_children
    
    
    def __repr__( self ):
        return "TreeItemInfo(item = {0}, data = {1}, first = {2})".format( repr( self.__item ), repr( self.__data ), repr( self.__add_children ) )


class TreeView:
    """
    ABSTRACT

    Manages a collection of data against a set of treeview items

    The derived class must implement virtual_update_item to decorate the items!
    """
    
    
    class __LoadingNodeData:
        pass
    
    
    def __init__( self, widget: QTreeWidget ):
        """
        CONSTRUCTOR
        """
        assert isinstance( widget, QTreeWidget )
        
        self._widget = widget
        self._resize_on_expand = None
        self._auto_scroll = False
        
        # noinspection PyUnresolvedReferences
        self._widget.itemExpanded[QTreeWidgetItem].connect( self.__on_widget_itemExpanded )
    
    
    @exceptToGui()
    def __on_widget_itemExpanded( self, item: QTreeWidgetItem ):
        if item.childCount( ) == 1 and self.item_data( item.child( 0 ) ) is self.__LoadingNodeData:
            self.update_item( item, rebuild_children = True )
        
        if self._resize_on_expand:
            self.resize_columns( )
    
    
    def __add_loading_node( self, item: QTreeWidgetItem ):
        """
        Adds a "loading node" to the item.
        When the item is expanded the loading node will be removed and `virtual_add_child_items` will be called.
        """
        item = self.add_item( item, self.__LoadingNodeData, update = False )
        item.setText(0, "(placeholder - should not be visible)")
    
    
    def readd_item( self, item: QTreeWidgetItem ) -> QTreeWidgetItem:
        """
        Removes an item from the tree-view and readds it
        """
        data = self.item_data( item )
        parent = item.parent( )
        self.remove_item( item )
        return self.add_item( parent, data )
    
    
    def add_item( self, parent: Optional[ QTreeWidgetItem ], data: object, update = True, loader = False ) -> QTreeWidgetItem:
        """
        Creates a new item with the specified data
        
        :param parent: Parent of the item, or None for root 
        :param data: Data associated with the item 
        :param update: Cause an update as soon as the item is added 
        :param loader: The item will not be updated with children. When `True`, the update function will be called to add the children. 
        :return: The item added 
        """
        
        assert data is not None
        
        item = QTreeWidgetItem( )
        item.setData( 0, Qt.UserRole, data )
        
        if parent:
            parent.addChild( item )
        else:
            self._widget.addTopLevelItem( item )
        
        if update:
            self.update_item( item, rebuild_children = not loader )
        
        if loader:
            self.__add_loading_node( item )
        
        self.autoscroll_to( item )
        
        return item
    
    
    def set_auto_scroll( self, value ):
        self._auto_scroll = value
        
        if value:
            if self._widget.topLevelItemCount( ) != 0:
                self.autoscroll_to( self._widget.topLevelItem( self._widget.topLevelItemCount( ) - 1 ) )
    
    
    def set_auto_scroll_button( self, button: QAbstractButton ):
        def f( checked ):
            self.set_auto_scroll( checked )
        
        
        button.setChecked( True )
        self._auto_scroll = True
        
        # noinspection PyUnresolvedReferences
        button.toggled.connect( f )
    
    
    def auto_scroll( self ):
        return self._auto_scroll
    
    
    def rebuild_selected_item( self ):
        """
        Rebuilds the item the user-selection is on.
        """
        item = self._widget.currentItem( )
        
        if item:
            self.update_item( item )
    
    
    @abstract
    def virtual_update_item( self, info: TreeItemInfo ) -> None:
        """
        Updates the specified item
        """
        raise NotImplementedError( "abstract" )
    
    
    def update_item( self, item: Optional[ QTreeWidgetItem ], rebuild_children = False, update_tag = None ) -> None:
        if item is not None:
            if rebuild_children:
                while item.childCount( ):
                    item.removeChild( item.child( item.childCount( ) - 1 ) )
            
            try:
                self.virtual_update_item( TreeItemInfo( item, self.item_data( item ), rebuild_children, update_tag ) )
            except Exception as ex:
                print_helper.print_exception( ex )
                raise
    
    
    def autoscroll_to( self, item ):
        """
        Scrolls to the specified item IF auto-scroll is enabled.
        """
        if self._auto_scroll:
            self.widget.setCurrentItem( item )
    
    
    @staticmethod
    def item_path( item: Optional[ QTreeWidgetItem ] ) -> Optional[ List[ QTreeWidgetItem ] ]:
        """
        Gets the sequence of ancestors for the specified item, including the item itself
        """
        if item is None:
            return None
        
        results = [ ]
        
        while item:
            results.append( item )
            item = item.parent( )
        
        return list( reversed( results ) )
    
    
    def data_path( self, item: Optional[ QTreeWidgetItem ] ) -> Optional[ List[ UiInfoProperty ] ]:
        """
        As item_path, but returns the data of the items rather than the items themselves
        """
        path = self.item_path( item )
        
        if path is None:
            return None
        
        return cast(List[UiInfoProperty], [ self.item_data( x ) for x in path ])
    
    
    def remove_item_by_data_path( self, path: List[ object ] ) -> List[ QTreeWidgetItem ]:
        """
        Removes the item at the end of the path
        :return: 
        """
        
        item_path = self.find_item_path_by_data_path( path )
        
        if item_path is not None:
            self.remove_item( item_path[ -1 ] )
        
        return item_path
    
    
    def ensure_branch_exists( self, data: List[ object ], update_items = True ) -> List[ QTreeWidgetItem ]:
        """
        Ensures the branch (data[0]/data[1]/data[2]...) exists in the tree, creating items as necessary
        :return: The list of items in the branch
        """
        
        results = [ ]
        item = None
        
        for datum in data:
            child = self.find_child_by_data( item, datum )
            
            if not child:
                child = self.add_item( item, datum, update_items )
            
            item = child
            results.append( item )
        
        return results
    
    
    def data_path_by_data( self, data ) -> Optional[ List[ object ] ]:
        """
        As data_path, but finds the item corresponding to the data first
        """
        item = self.find_item_by_data( data )
        
        if item is None:
            return None
        
        return self.data_path( item )
    
    
    @property
    def widget( self ):
        """
        Returns the QT widget
        """
        return self._widget
    
    
    def delete_selected_item( self ) -> bool:
        """
        Deletes the user-selected item
        """
        item = self._widget.currentItem( )
        
        if item:
            self.remove_item( item )
            return True
        
        return False
    
    
    def selected_item( self ) -> Optional[ QTreeWidgetItem ]:
        """
        Returns the user-selected item
        """
        return self._widget.currentItem( )
    
    
    def selected_data( self ) -> Optional[ object ]:
        """
        Returns the data associated with the user-selected item
        :return:
        """
        item = self._widget.currentItem( )
        
        if not item:
            return None
        
        return self.item_data( item )
    
    
    def remove_item( self, item: QTreeWidgetItem ):
        """
        Removes the specified item, wherever it may be in the tree
        """
        if item.parent( ):
            item.parent( ).takeChild( item.parent( ).indexOfChild( item ) )
        else:
            self._widget.takeTopLevelItem( self._widget.indexOfTopLevelItem( item ) )
    
    
    @staticmethod
    def item_data( item: QTreeWidgetItem ) -> object:
        """
        Gets the data associated with the specified item
        """
        return item.data( 0, Qt.UserRole )
    
    
    @staticmethod
    def item_extra_data( item: QTreeWidgetItem, index = 1 ) -> object:
        """
        Gets the data associated with the specified item
        """
        return item.data( 0, Qt.UserRole + index )
    
    
    @staticmethod
    def item_set_extra_data( item: QTreeWidgetItem, value, index = 1 ) -> object:
        """
        Gets the data associated with the specified item
        """
        return item.setData( 0, Qt.UserRole + index, value )
    
    
    def remove_item_by_data( self, data ) -> bool:
        """
        Removes the item with the specified data
        """
        item = self.find_item_by_data( data )
        
        if not item:
            raise ValueError( "Cannot find item: " + str( data ) )
        
        if item:
            self.remove_item( item )
            return True
        
        return False
    
    
    def find_child_by_data( self, item: Optional[ QTreeWidgetItem ], data ) -> Optional[ QTreeWidgetItem ]:
        """
        Finds the child of an item with the specified data
        This is not a recursive search, for a recursive search use find_item_by_data.
        """
        for child in self.child_items( item ):
            if self.item_data( child ) == data:
                return child
        
        return None
    
    
    def find_item_by_data( self, data ) -> Optional[ QTreeWidgetItem ]:
        """
        Finds an item by its data (returns an index-item tuple)
        """
        
        for item in self.all_items( ):
            if self.item_data( item ) == data:
                return item
        
        return None
    
    
    def find_item_path_by_data_path( self, path: List[ object ] ) -> Optional[ List[ QTreeWidgetItem ] ]:
        result = [ ]
        
        item = None
        
        for data in path:
            item = self.find_child_by_data( item, data )
            
            if item is None:
                return None
            
            result.append( item )
        
        return result
    
    
    def child_items( self, item: Optional[ QTreeWidgetItem ] ) -> Iterator[ QTreeWidgetItem ]:
        """
        Returns an iterator over the child-items.
        :param item: Item or NONE for root.
        """
        
        if item is None:
            for i in range( self._widget.topLevelItemCount( ) ):
                yield self._widget.topLevelItem( i )
        else:
            for i in range( item.childCount( ) ):
                yield item.child( i )
    
    
    def resize_columns( self ):
        for i in range( self._widget.columnCount( ) ):
            self._widget.resizeColumnToContents( i )
    
    
    def all_items( self ) -> Iterator[ QTreeWidgetItem ]:
        for i in range( self._widget.topLevelItemCount( ) ):
            yield from self._all_items( self._widget.topLevelItem( i ) )
    
    
    def _all_items( self, item: QTreeWidgetItem ) -> Iterator[ QTreeWidgetItem ]:
        yield item
        
        for i in range( item.childCount( ) ):
            child = item.child( i )
            yield from self._all_items( child )
    
    
    def checked_items( self ) -> Iterator[ QTreeWidgetItem ]:
        """
        All checked items
        """
        for item in self.all_items( ):
            if item.checkState( 0 ) == Qt.Checked:
                yield item
    
    
    def checked_data( self ) -> Iterator[ object ]:
        for item in self.checked_items( ):
            yield self.item_data( item )
    
    
    def set_resize_on_expand( self, value: bool = True ):
        """
        Tells the tree-view to resize when columns are expanded
        """
        self._resize_on_expand = value
    
    
    def set_columns( self, *args ):
        """
        Sets the column headers
        """
        self._widget.setColumnCount( len( args ) )
        
        for i, v in enumerate( args ):
            self._widget.headerItem( ).setText( i, v )
    
    
    def clear( self ):
        self._widget.clear( )
