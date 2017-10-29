# coding=utf-8
import re

from .custom_types import FieldDisplayName, FieldDataType
from .utils import rebracket

_NON_FORMULA_PATTERN = re.compile(r"^[\w|\s]+$")


class SqlField:
    """Value-object representing a field in a relational database"""

    def __init__(self,
        alias: FieldDisplayName,
        definition: str,
        data_type: FieldDataType=FieldDataType.STRING,
        editable: bool=True,
        visible: bool=True
    ):

        self._alias = alias
        self._definition = definition
        self._data_type = data_type
        self._editable = editable
        self._visible = visible

    @property
    def alias(self) -> str:
        """Column heading to display to the user"""
        return rebracket(self._alias)

    @property
    def data_type(self) -> FieldDataType:
        """Field data type"""
        return self._data_type

    @property
    def definition(self) -> str:
        """Name (or formula) of the field within the Subqueries SQL attribute.

        If the definition is a formula, then don't wrap it in brackets.

        :return: SQL string representation of a field in a Subquery
        """
        if _NON_FORMULA_PATTERN.match(rebracket(self._definition)):
            return rebracket(self._definition)
        return self._definition

    @property
    def editable(self) -> bool:
        """Is the field editable?"""
        return self._editable

    @property
    def full_name_with_alias(self) -> str:
        """[Subquery Alias].[Field Display Name] AS [Field Alias]"""
        return f"{self.definition} AS {self.alias}"

    @property
    def visible(self) -> bool:
        """Is the field visible?"""
        return self._visible

    def __hash__(self):
        return hash(self.alias)

    def __eq__(self, other):
        return self.alias == other.alias

    def __str__(self):
        return f"""
            SqlField:
                alias:      {self._alias!s}
                definition: {self._definition!s}
                data_type:  {self._data_type!s}
                editable:   {self._editable!s}
                visible:    {self._visible!s}
        """

    def __repr__(self):
        return f"""=
            SqlField(
                alias={self._alias!r},
                definition={self._definition!r},
                data_type={self._data_type!r},
                editable={self._editable!r},
                visible={self._visible!r}
        )"""
