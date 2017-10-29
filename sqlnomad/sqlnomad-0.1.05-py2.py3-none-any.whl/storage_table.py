# coding=utf-8
from itertools import chain
from typing import Sequence, Tuple

from .custom_types import (
    TableStorageName,
    TableDisplayName,
    SqlDialect,
    FieldDisplayName,
    SQL,
    SqlRow,
    SqlValue,
    PrimaryKeyValue
)
from .iqueryable import IQueryable
from .sql_field import SqlField
from .storage_field import StorageField
from .utils import rebracket


class StorageTable(IQueryable):
    """Value-object representing a table in a relational database"""

    def __init__(self,
        storage_name:      TableStorageName,
        display_name:      TableDisplayName,
        fields:            Sequence[StorageField],
        dialect:           SqlDialect,
        schema:            str=None,
        primary_key_alias: FieldDisplayName=None,
        editable:          bool=True
    ):

        self._storage_name = storage_name
        self._display_name = display_name
        self._fields = fields
        self._dialect = dialect
        self._schema = schema
        self._primary_key_alias = primary_key_alias
        self._editable = editable

    @property
    def alias(self) -> FieldDisplayName:
        return rebracket(self._display_name)

    @property
    def dialect(self) -> SqlDialect:
        return self._dialect

    @property
    def editable(self) -> bool:
        return self._editable

    @property
    def fields(self) -> Sequence[SqlField]:
        return [
            SqlField(
                alias=rebracket(fld.display_name),
                definition=f"{rebracket(self.alias)}.{rebracket(fld.display_name)}",
                data_type=fld.data_type,
                visible=fld.visible
            )
            for fld in self._fields
        ]

    @property
    def root_alias(self) -> str:
        return rebracket(self._display_name)

    @property
    def schema(self) -> str:
        return rebracket(self._schema)

    @property
    def sql(self) -> SQL:
        if self._schema:
            full_table_name = f"{rebracket(self._schema)}.{rebracket(self._storage_name)}"
        else:
            full_table_name = rebracket(self._storage_name)

        qualify_field = lambda fld: f"{rebracket(fld.storage_name)} AS {rebracket(fld.display_name)}"
        select_fields = ", ".join(qualify_field(fld) for fld in self._fields)

        return f"SELECT {select_fields} FROM {full_table_name}"

    @property
    def suffix(self) -> int:
        return 1

    def add_row(self, row: SqlRow) -> Tuple[SQL, Sequence[SqlValue]]:
        if not self._editable:
            raise AttributeError(f"{self._storage_name} not set as editable.")

        if not self._primary_key_alias:
            raise AttributeError(f"No id field specified for table {self._storage_name!r}")

        editable_fields = {
            alias: val for alias, val in row.items()
            if alias != self._primary_key_alias and self.field(field_alias=alias).editable
        }

        field_list = ", ".join(
            rebracket(fld.storage_name)
            for fld in self._fields
            if fld.display_name in editable_fields.keys()
        )

        return f"""
            INSERT INTO {rebracket(self._storage_name)} ({field_list})
            VALUES ({', '.join("?"*len(editable_fields))})
        """, tuple(editable_fields.values())

    def delete_row(self, primary_key_value: int) -> Tuple[SQL, PrimaryKeyValue]:
        if not self._editable:
            raise AttributeError(f"{self._storage_name} not set as editable.")

        if primary_key_value is None:
            raise ValueError("The primary key value provides was None")

        try:
            id_storage_name = next(
                fld.storage_name for fld in self._fields
                if fld.display_name == self._primary_key_alias
            )
        except StopIteration:
            raise ValueError(
                f"No primary key named {self._primary_key_alias} was found.")

        return f"""
            DELETE FROM {rebracket(self._storage_name)} 
            WHERE {rebracket(id_storage_name)} = ?
        """, str(primary_key_value)

    def field(self, field_alias: FieldDisplayName) -> SqlField:
        try:
            return next(
                fld for fld in self.fields
                if fld.alias == rebracket(field_alias)
            )
        except StopIteration:
            raise ValueError(f"No field named {field_alias!r} was found on {self._display_name!r}.")

    def update_row(self, primary_key_value: PrimaryKeyValue, row: SqlRow) -> Tuple[SQL, PrimaryKeyValue]:
        if not self._editable:
            raise AttributeError(f"{self._storage_name} not set as editable.")

        if not self._primary_key_alias:
            raise AttributeError(f"No id field specified for table {self._storage_name!r}")

        if primary_key_value is None:
            raise ValueError(f"{primary_key_value} is not a valid primary key value.")

        try:
            id_storage_name = next(
                fld.storage_name for fld in self._fields
                if fld.display_name == self._primary_key_alias
            )
        except StopIteration:
            raise ValueError(
                f"No primary key named {self._primary_key_alias} was found.")

        non_id_fields = {
            fld: val for fld, val in row.items()
            if fld != self._primary_key_alias
        }
        set_fields = ", ".join(
            f"{rebracket(fld.storage_name)} = ?"
            for fld in self._fields
            if fld.display_name in non_id_fields.keys()
        )

        return f"""
            UPDATE {rebracket(self._storage_name)} 
            SET {set_fields}
            WHERE {rebracket(id_storage_name)} = ?
        """, tuple(chain(non_id_fields.values(), [primary_key_value]))

    alias.__doc__ = IQueryable.__doc__
    dialect.__doc__= IQueryable.__doc__
    fields.__doc__ = IQueryable.__doc__
    root_alias.__doc__ = IQueryable.__doc__
    schema.__doc__ = IQueryable.__doc__
    sql.__doc__ = IQueryable.__doc__
    field.__doc__ = IQueryable.__doc__

    def __repr__(self):
        return f"""
        StorageTable(
            storage_name={self._storage_name!r},
            display_name={self._display_name!r},
            fields={self._fields!r},
            dialect={self._dialect!r},
            schema={self._schema!r}
        )
        """

    def __str__(self):
        return f"""
        StorageTable
            storage_name: {self._storage_name!s}
            display_name: {self._display_name!s}
            fields: {self._fields!s}
            dialect: {self._dialect!s}
            schema: {self._schema!s}
        """

