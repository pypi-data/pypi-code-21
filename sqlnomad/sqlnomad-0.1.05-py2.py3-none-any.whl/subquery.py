# coding=utf-8
from typing import Sequence, Counter

from .custom_types import (
    TableDisplayName,
    SqlDialect,
    SQL,
    FieldDisplayName
)
from .iqueryable import IQueryable
from .sql_field import SqlField
from .utils import rebracket, strip_chars


def _check_for_duplicate_field_aliases(fields: Sequence[SqlField]) -> Sequence[SqlField]:
    aliases = (fld.alias for fld in fields)
    duplicates = [
        alias
        for alias, ct in Counter(aliases).items()
        if ct > 1
    ]
    if duplicates:
        raise UserWarning(f"Duplicate field aliases found {duplicates}")
    return fields


class Subquery(IQueryable):
    """Value-object representing a SQL subquery with its accompanying field metadata

    :param sql:     SQL statement of the subquery
                    This parameter can be either a SQL statement or a table
                    storage name.
    :param fields:  Set of SqlFields for the subquery
    :param dialect: SqlDialect of the underlying table (eg, SqlDialect.MSSQL)
    :param alias:   Name to refer to the current subquery in outer scopes
    :param schema:  The database schema of the underlying table.
                    This parameter is only relevant when the SQL parameter is
                    simply the name of a table.
    :param suffix:  Suffix to append to the alias of the subquery to
                    distinguish it from subqueries in outer scopes with the
                    same alias.
    """
    def __init__(self,
        sql: TableDisplayName,
        fields: Sequence[SqlField],
        dialect: SqlDialect,
        alias: TableDisplayName,
        schema: str=None,
        suffix: int=1
    ):
        self._sql = sql
        self._fields = _check_for_duplicate_field_aliases(fields)
        self._dialect = dialect
        self._alias = alias
        self._schema = schema
        self._suffix = suffix

    @property
    def alias(self) -> str:
        return rebracket(f"{self._alias} {self._suffix}")

    @property
    def dialect(self) -> SqlDialect:
        return self._dialect

    @property
    def fields(self) -> Sequence[SqlField]:
        return [
            SqlField(
                definition=f"{self.alias}.{fld.alias}",
                alias=fld.alias,
                data_type=fld.data_type,
                visible=fld.visible
            )
            for fld in self._fields
        ]

    @property
    def root_alias(self) -> TableDisplayName:
        return self._alias

    @property
    def schema(self) -> str:
        if self._schema:
            return rebracket(self._schema)

    @property
    def suffix(self) -> int:
        return self._suffix

    @property
    def sql(self) -> SQL:
        return self._sql

    def field(self, field_alias: FieldDisplayName) -> SqlField:
        std_alias = lambda a: strip_chars(a, "[]").lower()
        try:
            return next(
                fld for fld in self.fields
                if std_alias(fld.alias) == std_alias(rebracket(field_alias))
            )
        except StopIteration:
            raise ValueError(f"No field named {field_alias} was found on the {self.alias} table.")

    alias.__doc__ = IQueryable.__doc__
    dialect.__doc__= IQueryable.__doc__
    fields.__doc__ = IQueryable.__doc__
    root_alias.__doc__ = IQueryable.__doc__
    schema.__doc__ = IQueryable.__doc__
    sql.__doc__ = IQueryable.__doc__
    field.__doc__ = IQueryable.__doc__

    def __str__(self):
        return f"{self._sql} {rebracket(self._alias)}"

    def __repr__(self):
        return f"""
            RawSqlTable(
                sql={self._sql!r},
                fields={self._fields!r},
                dialect={self._dialect!r},
                alias={self._alias!r},
                schema={self._schema!r},
                suffix={self._suffix!r}
            )
            """
