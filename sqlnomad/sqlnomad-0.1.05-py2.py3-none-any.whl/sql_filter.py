# coding=utf-8
from typing import NamedTuple

from .custom_types import FilterOperator, SqlValue, FieldDisplayName


class SqlFilter(NamedTuple):
    """Value-object representing a SQL where clause statement"""

    field_alias: FieldDisplayName
    operator: FilterOperator
    value: SqlValue

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __lt__(self, other):
        return self.field_alias < other.field_alias

    def __repr__(self):
        return f"""
        SqlFilter(
            field={self.field_alias!r}, 
            operator={self.operator!r}, 
            value={self.value!r}
        )"""

    def __str__(self):
        return f"{self.field_alias} {self.operator} {self.value!r}"
