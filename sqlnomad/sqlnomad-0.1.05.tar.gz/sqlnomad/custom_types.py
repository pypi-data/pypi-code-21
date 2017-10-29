# coding=utf-8
from enum import Enum
from typing import NewType, Union, Optional, Sequence, Dict

import datetime

FieldDisplayName = NewType("FieldDisplayName", str)
FieldStorageName = NewType("FieldStorageName", str)
PrimaryKeyValue = NewType("PrimaryKeyValue", int)
SQL = NewType("SQL", str)
SqlValue = Optional[Union[bool, str, int, float, datetime.date, datetime.datetime]]
SqlRow = Dict[FieldDisplayName, SqlValue]
SqlRows = Sequence[SqlRow]
TableDisplayName = NewType("TableDisplayName", str)
TableStorageName = NewType("TableStorageName", str)


class AggregationMethod(Enum):
    """Method for aggregating an AggregateField"""
    AVG = "Average"
    COUNT = "Count"
    MAX = "Maximum"
    MIN = "Minimum"
    SUM = "Total"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class FieldDataType(Enum):
    BOOLEAN = "boolean"
    DATE = "date"
    FLOAT = "float"
    STRING = "string"
    INTEGER = "integer"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"FieldDataType.{self.name}"


class FilterOperator(Enum):
    CONTAINS = "Contains"
    ENDS_WITH = "Ends With"
    EQUALS = "Equals"
    GREATER_THAN = "Greater Than"
    GREATER_THAN_OR_EQUAL_TO = "Greater Than or Equal To"
    LESS_THAN = "Less Than"
    LESS_THAN_OR_EQUAL_TO = "Less Than or Equal To"
    STARTS_WITH = "Starts With"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class SortOrder(Enum):
    ASCENDING = "Ascending"
    DESCENDING = "Descending"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class SqlDialect(Enum):
    ACCESS = "access"
    MSSQL = "mssql"
    MYSQL = "mysql"
    ORACLE = "oracle"
    POSTGRES = "postgres"
    SQLITE = "sqlite"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

