from mhelper.comment_helper import override
from mhelper.string_helper import timedelta_to_string



from PyQt5.QtWidgets import QAbstractButton


from datetime import datetime
from typing import Dict, Set

from PyQt5.QtWidgets import QProgressBar, QTreeWidget, QTreeWidgetItem

from intermake.engine.progress_reporter import UpdateInfo
from intermake.hosts.frontends.gui_qt.views.tree_view import TreeItemInfo, TreeView


__author__ = "Martin Rusilowicz"


_COL_INDEX = 0
_COL_TIME = 1
_COL_THREAD = 2
_COL_STATUS = 3
_COL_PROGRESS = 4

class ProgressView( TreeView ):
    """
    Treeview for logs
    """
    @override
    def virtual_update_item( self, info: TreeItemInfo ) -> None:
        """
        OVERRIDE
        Never called
        """
        pass


    def __init__( self, widget: QTreeWidget, auto_scroll_button:QAbstractButton ):
        super( ).__init__( widget )
        self._index = 0
        self._start = datetime.now( )

        widget.setColumnCount( 5 )
        widget.headerItem( ).setText( _COL_INDEX, "Index" )
        widget.headerItem( ).setText( _COL_TIME, "Time" )
        widget.headerItem( ).setText( _COL_THREAD, "Thread" )
        widget.headerItem( ).setText( _COL_STATUS, "Status" )
        widget.headerItem( ).setText( _COL_PROGRESS, "Progress" )

        widget.setColumnWidth( _COL_INDEX, 128 )
        widget.setColumnWidth( _COL_TIME, 128 )
        widget.setColumnWidth( _COL_THREAD, 64 )
        widget.setColumnWidth( _COL_STATUS, 256 )
        widget.setColumnWidth( _COL_PROGRESS, 256 )

        self._last_items = { }  # type:Dict[int, QTreeWidgetItem]

        self._multiple_threads = False
        
        self.set_auto_scroll_button(auto_scroll_button)


    def add_comment( self, left: str, right: str ):
        item = QTreeWidgetItem( )
        item.setText( _COL_INDEX, "-" )  # index
        item.setText( _COL_TIME, self._time( ) )  # time
        item.setText( _COL_THREAD, "UI" )  # thread
        item.setText( _COL_STATUS, left )  # status
        item.setText( _COL_PROGRESS, right )  # progress
        self.widget( ).addTopLevelItem( item )
        self.autoscroll_to( item )


    def add( self, info: UpdateInfo ):
        self._index += 1
        thread = info.thread_index

        if thread:
            self._multiple_threads = True

        item = super( ).ensure_branch_exists( info.depth, update_items = False )[ -1 ]

        item_xdata = super( ).item_extra_data( item )  # type:Set[int]

        if item_xdata is None:
            item_xdata = set( )
            super( ).item_set_extra_data( item, item_xdata )

        if thread in self._last_items:
            last_item = self._last_items[ thread ]
            last_item_xdata = super( ).item_extra_data( last_item )  # type:Set[int]
            last_item_xdata.remove( thread )
            last_item.setText( _COL_THREAD, "".join( str( x ) for x in last_item_xdata ) )

        self._last_items[ thread ] = item
        item_xdata.add( thread )

        if info.max > 0:
            progress = info.value / info.max
        else:
            progress = 0

        item.setText( _COL_INDEX, str( self._index ) )  # index
        item.setText( _COL_TIME, self._time( ) )  # time

        if self._multiple_threads:
            item.setText( _COL_THREAD, "".join( str( x ) for x in item_xdata ) )  # thread
        else:
            item.setText( _COL_THREAD, "".join( "-->" for _ in item_xdata ) )  # thread

        item.setText( _COL_STATUS, str( info.text ) )  # status

        if progress > 0:
            progress_bar = self.widget( ).itemWidget( item, _COL_PROGRESS )  # progress

            if not progress_bar:
                progress_bar = QProgressBar( )
                progress_bar.setMaximum( 100 )
                self.widget( ).setItemWidget( item, _COL_PROGRESS, progress_bar )

            progress_bar.setValue( int( progress * 100 ) )

        while self.widget( ).topLevelItemCount( ) > 100:
            self.widget( ).takeTopLevelItem( 0 )

        super().autoscroll_to( item )


    def _time( self ) -> str:
        return timedelta_to_string(datetime.now( ) - self._start )


    


    def set_auto_scroll( self, value: bool ):
        self._auto_scroll = value


    def auto_scroll( self ):
        return self._auto_scroll
