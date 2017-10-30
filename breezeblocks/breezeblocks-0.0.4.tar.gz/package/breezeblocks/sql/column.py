"""Provides a column class and an expression for using columns in queries."""
from .expressions import _ValueExpr

class ColumnExpr(_ValueExpr):
    """Represents a database column."""
    
    def __init__(self, name, table):
        """Initializes a column.
        
        :param name: The name of this column.
        
        :param table: The table to which this column belongs.
        """
        self.name = name
        
        self.table = table
        self.full_name = '.'.join([table.name, self.name])
    
    def _get_name(self):
        """Provides the unqualifed column name as the select field name."""
        return self.name
    
    def _get_ref_field(self):
        """Returns a way to reference this column in a query."""
        return self.full_name
    
    def _get_select_field(self):
        """Returns the expression for selecting this column in a query."""
        return self.full_name
    
    def _get_tables(self):
        """Returns a set containing the table this column is from."""
        return set((self.table,))
    
    def as_(self, alias):
        """Provides a different alias for the same underlying column.
        
        :param alias: Another alias to use.
        """
        return AliasedColumnExpr(alias, self)

class AliasedColumnExpr(_ValueExpr):
    """A column with an alias used in querying."""
    
    def __init__(self, alias, column):
        """Initializes an aliased column from an existing column.
        
        :param alias: The alias that will be assigned to this object.
        
        :param column: The :class:`Column` that this is going to reference.
        """
        self.column = column
        self._alias = alias
    
    @property
    def full_name(self):
        """Returns the full name of the underlying column."""
        return self.column.full_name
    
    def _get_name(self):
        return self._alias
    
    def _get_ref_field(self):
        """Returns a way to reference this column in a query."""
        return self.full_name
    
    def _get_select_field(self):
        """Returns the expression for selecting this column in a
        query."""
        return '{} AS {}'.format(
            self.full_name, self._alias)
    
    def _get_tables(self):
        return self.column._get_tables()
    
    def as_(self, alias):
        """Provides a different alias for the same underlying column.
        
        :param alias: Another alias to use.
        """
        return AliasedColumnExpr(alias, self.column)
