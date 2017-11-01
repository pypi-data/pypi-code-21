"""
Draws tables
"""

from typing import Callable, List, Optional
from mhelper import array_helper

from intermake.engine import m_print_helper
from intermake.engine.environment import MENV
from intermake.visualisables.visualisable import UiInfo, EColour, IVisualisable
from intermake.hosts.frontends.gui_qt.designer import resources



if True:
    VERTICAL_BAR = "│"
    HORIZONTAL_BAR = "─"
    BAR_CT = "┼"
    BAR_TL = "┌"
    BAR_TT = "┬"
    BAR_TR = "┐"
    BAR_BR = "┘"
    BAR_BL = "└"
    BAR_BT = "┴"
    BAR_LT = "├"
    BAR_RT = "┤"
else:
    VERTICAL_BAR = "|"
    HORIZONTAL_BAR = "-"
    BAR_CT = "+"
    BAR_TL = "+"
    BAR_TT = "+"
    BAR_TR = "+"
    BAR_BR = "+"
    BAR_BL = "+"
    BAR_BT = "+"
    BAR_LT = "+"
    BAR_RT = "+"

SPACER = " "
SPACER_LENGTH = len( SPACER )

HLINE = "----"
NEW_TABLE = "____"


class Table( IVisualisable ):
    """
    This is essentially a list with a special __str__ function, handled by make_table.
    
    Suitable for pickling, it doesn't contain any extra data.
    """
    
    
    
    
    def visualisable_info( self ) -> UiInfo:
        value = "Table of {0} rows and {1} columns".format( len( self.rows ), self.num_cols() )
        
        return UiInfo( name = str(self),
                       comment = self.to_string(),
                       type_name = "Table",
                       value = value,
                       colour = EColour.MAGENTA,
                       icon = resources.list,
                       extra = { "rows": self.rows } )
    
    
    def num_cols( self ) -> int:
        return max( len( x ) for x in self.rows )
    
    
    def num_rows( self ) -> int:
        return len( self.rows )
    
    
    def num_cells( self ) -> int:
        return self.num_rows() * self.num_cols()
    
    
    def __init__( self, name = None, pickle: bool = False ):
        self.name = name
        self.rows = [ ]  # type: List[List[Optional[object]]]
        self.pickle = pickle
    
    
    def add_row( self, *columns, check = None ):
        """
        Adds a row to the table
        :param columns: Column values 
        :param check: Check for picklablity 
        :return: Nothing 
        """
        if check is None:
            check = self.pickle
        
        if check:
            for i, x in enumerate( columns ):
                if type( x ) not in (int, str, float, bool, None):
                    raise ValueError( "Cannot add the type «{0}» to a table because it is either not picklable or hasn't been added to the list of picklable types. The offending object is «{1}» at column {2}.".format( type( x ).__name__, x, i ) )
        
        self.rows.append( list( columns ) )
    
    
    def add_rows_from_text( self, sep = "\n", *columns: str ):
        """
        Calls `add_rows` after splitting the text by `sep`.
        
        :param sep: Row delimiter in the text 
        :param columns: One argument per column 
        :return: Nothing 
        """
        to_add = [ ]
        
        for x in columns:
            to_add.append( x.split( sep ) )
        
        self.add_rows( to_add )
    
    
    def add_rows( self, *columns: List[ str ] ):
        """
        Appends rows to the table
        
        :param columns: One list per column, with each entry of that list corresponding to a row 
        :return: Nothing 
        """
        start_col = 0
        start_row = len( self.rows )
        
        for src_col_index, src_col in enumerate( columns ):
            for src_row_index, src_cell in enumerate( src_col ):
                dest_row = start_row + src_row_index
                dest_col = start_col + src_col_index
                self[ dest_row, dest_col ] = src_cell
    
    
    def __len__( self ):
        return self.num_rows()
    
    
    def add_hline( self ):
        """
        Appends a horizontal line to the table
        """
        self.rows.append( [ HLINE ] )
    
    
    def add_title( self, title ):
        """
        Appends a title to the table
        """
        self.rows.append( [ title ] )
        self.rows.append( [ HLINE ] )
    
    
    def to_string( self, indent: int = 0, wrap_value = 80, min_col_width = 1 ):
        return make_table( self.rows, indent, wrap_value, min_col_width )
    
    
    def __str__( self ):
        if self.name:
            return self.name
        
        if self[ 0, 0 ]:
            return self[ 0, 0 ]
        
        return "Untitled"
    
    
    def __getitem__( self, key ):
        row_index = key[ 0 ]
        col_index = key[ 1 ]
        
        if row_index < 0 or row_index >= len( self.rows ):
            return None
        
        the_row = self.rows[ row_index ]
        
        if col_index < 0 or col_index >= len( the_row ):
            return None
        
        return the_row[ col_index ]
    
    
    def __setitem__( self, key, value ):
        row_index = key[ 0 ]
        col_index = key[ 1 ]
        
        array_helper.ensure_capacity( self.rows, row_index, [ ] )
        array_helper.ensure_capacity( self.rows[ row_index ], col_index )
        
        self.rows[ row_index ][ col_index ] = value
    
    
    @classmethod
    def from_object( cls, x ):
        t = Table()
        
        t.add_title( type( x ).__name__ )
        
        for k, v in x.__dict__.items():
            if not k.startswith( "_" ):
                t.add_row( k, v )
        
        return t
    
    
    def column_index( self, column: Optional[ object ] ) -> int:
        """
        Returns the `column`, if it is an integer, otherwise finds the column with that value in the first row
        """
        if not isinstance( column, int ):
            column = self.rows[ 0 ].index( column )
        
        return column
    
    
    def sort( self, column, headers, expression: Optional[ Callable[ [ Optional[ object ] ], Optional[ object ] ] ] = None ):
        """
        Sorts the rows
        :param expression: Optional key representing how to filter values in the column 
        :param column: Column to sort by (name or index as passed to `column_index`)
        :param headers: Number of rows to skip 
        """
        column = self.column_index( column )
        
        if expression is None:
            self.rows[ headers: ] = sorted( self.rows[ headers: ], key = lambda x: x[ column ] )
        else:
            self.rows[ headers: ] = sorted( self.rows[ headers: ], key = lambda x: expression( x[ column ] ) )
    
    
    def format( self, column, headers, expression: Callable[ [ Optional[ object ] ], Optional[ object ] ] ):
        """
        Formats a column
        :param column: Column to format (name or index as passed to `column_index`)
        :param headers: Number of rows to skip 
        :param expression: Expression representing how to format the values
        """
        column = self.column_index( column )
        
        for row_index in range( headers, len( self ) ):
            self[ row_index, column ] = expression( self[ row_index, column ] )
    
    
    def filter( self, column, headers, expression: Callable[ [ Optional[ object ] ], bool ] ):
        """
        Filters the rows
        :param column: Column to filter on (name or index as passed to `column_index`)
        :param headers: Number of rows to skip 
        :param expression: Expression representing which rows to keep
        """
        column = self.column_index( column )
        
        row_index = headers
        
        while row_index < len( self ):
            cell = self[ row_index, column ]
            if not expression( cell ):
                del self.rows[ row_index ]
            else:
                row_index += 1


def bar( indent_, col_widths, left, centre, right ) -> str:
    results = [ ]
    results.append( indent_ + left )
    
    for i, wid in enumerate( col_widths ):
        if i != 0:
            results.append( centre )
        
        results.append( HORIZONTAL_BAR * (wid + SPACER_LENGTH * 2) )
    
    results.append( right + "\n" )
    
    return "".join( results )


def str_col( col ):
    if col is None:
        return ""
    else:
        return str( col )


def content( indent_, col_widths, col_content, left = VERTICAL_BAR, centre = VERTICAL_BAR, right = VERTICAL_BAR ) -> str:
    results = [ ]
    results.append( indent_ + left + SPACER )  # |...
    
    for i, wid in enumerate( col_widths ):
        col = str_col( col_content[ i ] ) if i < len( col_content ) else ""
        
        if i:
            results.append( SPACER + centre + SPACER )  # ...|...
        
        results.append( col.ljust( wid ) )  # xxx___
    
    results.append( SPACER + right + "\n" )  # ...|
    
    return "".join( results )


def title( indent_, col_widths, title_, left = VERTICAL_BAR, right = VERTICAL_BAR ):
    results = [ ]
    
    space = sum( col_widths ) + (len( col_widths ) - 1) * SPACER_LENGTH * 3
    
    results.append( indent_ + left + SPACER + str_col( title_ ).ljust( space ) + SPACER + right + "\n" )  # | xxx___ |
    
    return "".join( results )


def make_table( rows, indent: int = 0, wrap_value = None, min_col_width = 1 ) -> str:
    """
    Makes a "pretty" ASCII table
    :param rows: n rows of n columns. Use rows containing HLINE for horizontal lines. 
    :param indent: How much to indent the table
    :param wrap_value: How wide the table can be   
    :param min_col_width: Minimum width of a single column 
    :return: 
    
    
    """
    
    if wrap_value is None:
        try:
            wrap_value = MENV.host.console_width
        except:
            wrap_value = 80
    
    # Argument reformation
    for i, row in enumerate( rows ):
        if type( row ) is str:
            rows[ i ] = [ row ]
    
    # Constants
    indent_ = " " * indent
    
    # Count number of columns
    num_columns = 0
    
    for row in rows:
        num_columns = max( len( row ), num_columns )
    
    # Calculate column widths
    max_col_width = wrap_value // num_columns
    
    col_width = [ min_col_width ] * num_columns
    
    for row in rows:
        for i, col in enumerate( row ):
            for line in str_col( col ).split( "\n" ):
                col_width[ i ] = min( max( col_width[ i ], len( line ) ), max_col_width )
    
    # Wordwrap cells
    new_rows = [ ]
    
    for row in rows:
        row_index = len( new_rows )
        
        for i, col in enumerate( row ):
            true_row_index = row_index
            
            for line in m_print_helper.wrap( str_col( col ), col_width[ i ] ):
                if true_row_index >= len( new_rows ):
                    this_row = [ ]
                    new_rows.append( this_row )
                else:
                    this_row = new_rows[ true_row_index ]
                
                while i >= len( this_row ):
                    this_row.append( "" )
                
                this_row[ i ] = line
                true_row_index += 1
    
    # Write output
    results = [ ]
    
    prev_title = False
    is_first_row = True
    
    for j in range( len( new_rows ) ):
        row = new_rows[ j ]
        
        is_new_table = len( row ) == 1 and row[ 0 ] == NEW_TABLE
        is_hline = len( row ) == 1 and row[ 0 ] == HLINE
        is_title = len( row ) == 1 and not (is_hline or is_new_table)
        
        if is_new_table:
            results.append( bar( indent_, col_width, BAR_BL, BAR_BT, BAR_BR ) )
            results.append( "" )
            is_first_row = True
            continue
        
        if is_first_row:
            # First row gets a bar above it
            if is_title:
                results.append( bar( indent_, col_width, BAR_TL, HORIZONTAL_BAR, BAR_TR ) )
            else:
                results.append( bar( indent_, col_width, BAR_TL, BAR_TT, BAR_TR ) )
        
        if is_title:
            # Single cells span the width
            results.append( title( indent_, col_width, row[ 0 ] ) )
        elif is_hline:
            if prev_title:
                results.append( bar( indent_, col_width, BAR_LT, BAR_TT, BAR_RT ) )
            else:
                results.append( bar( indent_, col_width, BAR_LT, BAR_CT, BAR_RT ) )
        else:
            results.append( content( indent_, col_width, row ) )
        
        prev_title = is_title
        is_first_row = False
    
    # Bottom bar
    results.append( bar( indent_, col_width, BAR_BL, BAR_BT, BAR_BR ) )
    
    # Return results
    return "".join( results )
