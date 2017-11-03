from .query_components import TableExpression
from .expressions import _ValueExpr
from ..exceptions import QueryError

class _JoinColumn(_ValueExpr):
    """A column used through a join expression."""
    
    def __init__(self, join_expr, column_expr):
        self._join_expr = join_expr
        self._column_expr = column_expr
    
    def _get_name(self):
        return self._column_expr._get_name()
    
    def _get_ref_field(self):
        return self._column_expr._get_ref_field()
    
    def _get_select_field(self):
        return self._column_expr._get_select_field()
    
    def _get_tables(self):
        return set((self._join_expr,))

class _JoinedTable(object):
    """A table that is one side of a join expression."""
    
    def __init__(self, join_expr, table):
        self._join_expr = join_expr
        self._table = table
        
        self._column_exprs = {}
        for name, column_expr in self._table._column_exprs.items():
            self._column_exprs[name] = _JoinColumn(join_expr, column_expr)
    
    def getColumn(self, key):
        if isinstance(key, str):
            return self._column_exprs[key]
        else:
            raise TypeError('Tables require strings for lookup keys.')
    
    def _get_selectables(self):
        return tuple(self._column_exprs[k] for k in self._table._column_names)
    
    def _get_params(self):
        return self._table._get_params()
    
    def _get_from_field(self):
        return self._table._get_from_field()

class _Join(TableExpression):
    """Represents a join of two table expressions."""
    
    def __init__(self, left, right):
        """Creates a join for the left and right expressions."""
        self._left = _JoinedTable(self, left)
        self._right = _JoinedTable(self, right)
    
    @property
    def left(self):
        return self._left
    
    @property
    def right(self):
        return self._right
    
    def getColumn(self, key):
        if not isinstance(key, str):
            raise TypeError('Tables require strings for lookup keys.')
        
        if key in self._left._column_exprs:
            return self._left._column_exprs[key]
        elif key in self._right._column_exprs:
            return self._right._column_exprs[key]
        else:
            raise KeyError()
    
    def __hash__(self):
        return hash((self._left._table, self._right._table))
    
    def __eq__(self, other):
        if (isinstance(other, self.__class__)):
            return (
                self._left.table == other._left.table and
                self._right.table == other._right.table
            )
        else:
            return False
    
    def _get_selectables(self):
        selectables = []
        selectables.extend(self._left._get_selectables())
        selectables.extend(self._right._get_selectables())
        return selectables
    
    def _get_params(self):
        params = []
        params.extend(self._left._get_params())
        params.extend(self._right._get_params())
        return params
    
    def _get_join_expression(self):
        raise NotImplementedError()

class _QualifiedJoin(_Join):
    """Represents a join with a 'USING' or 'ON' condition."""
    
    def __init__(self, left, right, *, on=None, using=None):
        super().__init__(left, right)
        
        if on is None and using is None:
            raise QueryError(
            'Qualified Join statements must have an ON or a USING condition.')
        
        if on is not None and using is not None:
            raise QueryError(
                'Join statement cannot have both ON and USING conditions.')
        
        self._on_exprs = on
        self._using_fields = using
    
    def _get_from_field(self):
        return self._get_join_expression() + ' ' + self._get_join_condition()
    
    def _get_join_condition(self):
        if self._on_exprs is not None:
            return 'ON {}'.format(
                ', '.join(expr._get_ref_field() for expr in self._on_exprs))
        elif self._using_fields is not None:
            return 'USING ({})'.format(', '.join(self._using_fields))
        else:
            raise QueryError(
                'A join condition must be specified for qualified joins.')

class CrossJoin(_Join):
    """Represents a cross join of two table expressions."""
    
    def _get_from_field(self):
        return self._get_join_expression()
    
    def _get_join_expression(self):
        return '{} CROSS JOIN {}'.format(
            self._left._get_from_field(), self._right._get_from_field())

class InnerJoin(_QualifiedJoin):
    """Represents an inner join of two table expressions."""
    
    def _get_join_expression(self):
        return '{} INNER JOIN {}'.format(
            self._left._get_from_field(), self._right._get_from_field())

class LeftJoin(_QualifiedJoin):
    """Represents a left outer join of two table expressions."""
    
    def _get_join_expression(self):
        return '{} LEFT JOIN {}'.format(
            self._left._get_from_field(), self._right._get_from_field())

class RightJoin(_QualifiedJoin):
    """Represents a right outer join of two table expressions."""
    
    def _get_join_expression(self):
        return '{} RIGHT JOIN {}'.format(
            self._left._get_from_field(), self._right._get_from_field())

class OuterJoin(_QualifiedJoin):
    """Represents a full outer join of two table expressions."""
    
    def _get_join_expression(self):
        return '{} OUTER JOIN {}'.format(
            self._left._get_from_field(), self._right._get_from_field())
