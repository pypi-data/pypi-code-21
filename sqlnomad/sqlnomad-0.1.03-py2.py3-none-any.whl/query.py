# coding=utf-8
from typing import (
    Callable,
    Sequence,
    List,
    Tuple,
    Optional
)

from .custom_types import (
    FieldDisplayName,
    SQL,
    TableDisplayName,
    SqlDialect
)
from .iqueryable import IQueryable
from .sql_field import SqlField
from .subquery import Subquery


class Query(IQueryable):
    """Monad that composes SQL subqueries with transformation functions"""

    _lineage: List[Tuple[Subquery, Optional[Subquery]]] = []

    def __init__(self, subquery: IQueryable):
        self._subquery = subquery

        Query._lineage.append(([self._subquery], None))

    @property
    def alias(self) -> str:
        return self._subquery.alias

    @property
    def dialect(self) -> SqlDialect:
        return self._subquery.dialect

    @property
    def fields(self) -> Sequence[SqlField]:
        return self._subquery.fields

    @property
    def root_alias(self) -> TableDisplayName:
        return self._subquery.root_alias

    @property
    def schema(self) -> str:
        return self._subquery.schema

    @property
    def sql(self) -> SQL:
        return self._subquery.sql

    @property
    def suffix(self) -> int:
        return self._subquery.suffix

    def field(self, field_alias: FieldDisplayName) -> SqlField:
        return self._subquery.field(field_alias)

    def bind(self, fn: Callable[[IQueryable], Subquery]) -> "Query":
        new_subquery = fn(self._subquery)
        Query._lineage.append((new_subquery, self._subquery))
        return Query(new_subquery)

    alias.__doc__ = IQueryable.__doc__
    dialect.__doc__= IQueryable.__doc__
    fields.__doc__ = IQueryable.__doc__
    root_alias.__doc__ = IQueryable.__doc__
    schema.__doc__ = IQueryable.__doc__
    sql.__doc__ = IQueryable.__doc__
    field.__doc__ = IQueryable.__doc__

    def __str__(self):
        return f"""
        Query
            subquery: {self._subquery!s}
        """

    def __repr__(self):
        return f"Query(subquery={self._subquery!r})"
