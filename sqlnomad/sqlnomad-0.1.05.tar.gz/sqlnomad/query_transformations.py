# coding=utf-8
from itertools import chain
from typing import (
    Callable,
    Sequence,
    Dict,
    Union
)

from .custom_types import (
    AggregationMethod,
    FilterOperator,
    SQL,
    SortOrder,
    FieldDisplayName,
    FieldDataType
)
from .iqueryable import IQueryable
from .sql_field import SqlField
from .sql_filter import SqlFilter
from .subquery import Subquery


def _aggregate_field(
    field:       SqlField,
    aggregation: AggregationMethod
) -> SqlField:

    aggregate_functions = {
        AggregationMethod.AVG: "AVG({})",
        AggregationMethod.COUNT: "COUNT({})",
        AggregationMethod.MAX: "MAX({})",
        AggregationMethod.MIN: "MIN({})",
        AggregationMethod.SUM: "SUM({})"
    }

    p = aggregate_functions[aggregation]

    data_types = {
        AggregationMethod.AVG: FieldDataType.FLOAT,
        AggregationMethod.COUNT: FieldDataType.INTEGER,
        AggregationMethod.MAX: FieldDataType.FLOAT,
        AggregationMethod.MIN: FieldDataType.FLOAT,
        AggregationMethod.SUM: FieldDataType.FLOAT
    }

    number_types = (
        FieldDataType.FLOAT,
        FieldDataType.INTEGER
    )

    if not field.data_type in (number_types) and FieldDataType != AggregationMethod.COUNT:
        raise TypeError(f"""
            {field.data_type!s} is not a valid data type for an 
            {aggregation!s} operation.
        """)

    return SqlField(
        definition=p.format(field.definition),
        alias=field.alias,
        data_type=data_types[aggregation],
        visible=field.visible
    )


def aggregate(
    group_by_fields: Sequence[FieldDisplayName],
    aggregations: Dict[FieldDisplayName, AggregationMethod]
) -> Callable[[IQueryable], Subquery]:

    def inner(subquery: IQueryable) -> Subquery:
        gb_flds = [
            subquery.field(fld_name)
            for fld_name in group_by_fields
        ]
        agg_flds = [
            _aggregate_field(
                field=subquery.field(fld_name),
                aggregation=fn
            )
            for fld_name, fn in aggregations.items()
        ]
        fields = gb_flds + agg_flds
        select_clause = "SELECT " + ", ".join(
            fld.full_name_with_alias
            for fld in sorted(fields, key=lambda f: f.alias)
        )
        from_clause = f"FROM ({subquery.sql}) {subquery.alias}"
        group_by_clause = "GROUP BY " + ", ".join(
            fld.definition
            for fld in sorted(gb_flds, key=lambda f: f.alias)
        )

        return Subquery(
            sql=f"{select_clause} {from_clause} {group_by_clause}",
            fields=fields,
            dialect=subquery.dialect,
            alias=subquery.root_alias,
            suffix=subquery.suffix + 1
        )

    return inner


def order_columns(field_aliases: Sequence[FieldDisplayName]) -> Callable[[IQueryable], Subquery]:

    def inner(subquery: IQueryable):

        fields = [
            subquery.field(field_alias=field_alias)
            for field_alias in field_aliases
        ]

        qry = f"""
            SELECT {', '.join(
                fld.full_name_with_alias
                for fld in fields
            )}
            FROM ({subquery.sql}) {subquery.alias}
        """

        return Subquery(
            sql=qry,
            fields=fields,
            dialect=subquery.dialect,
            alias=subquery.root_alias,
            suffix=subquery.suffix + 1
        )

    return inner


def _filter_condition(field: SqlField, flt: SqlFilter) -> str:

    filter_patterns = {
        FilterOperator.CONTAINS:                 "{} LIKE '*{}*'",
        FilterOperator.EQUALS:                   "{} = '{}'",
        FilterOperator.STARTS_WITH:              "{} LIKE '{}%'",
        FilterOperator.ENDS_WITH:                "{} = '%{}'",
        FilterOperator.GREATER_THAN:             "{} > '{}'",
        FilterOperator.GREATER_THAN_OR_EQUAL_TO: "{} >= '{}'",
        FilterOperator.LESS_THAN:                "{} < '{}'",
        FilterOperator.LESS_THAN_OR_EQUAL_TO:    "{} <= '{}'"
    }
    return filter_patterns[flt.operator].format(field.definition, flt.value)


def find(filters: Sequence[Union[SqlFilter, list]]) -> Callable[[IQueryable], Subquery]:
    """Apply a where condition to the query

    If a sequence of sequences is provided, then each sequence is grouped using
    AND conditions, and the groups themselves are bound using OR conditions.
    eg: [[flt1, flt2], [flt3, flt4]] = (flt1 and flt2) or (flt3 and flt4)

    """
    def inner(subquery: IQueryable) -> Subquery:

        def unwrap(flt) -> SQL:
            if isinstance(flt, SqlFilter):
                return flt.sql
            elif isinstance(flt[0], SqlFilter):
                return "(" + " AND ".join(
                    _filter_condition(field=subquery.field(f.field_alias), flt=f)
                    for f in flt
                ) + ")"
            else:
                return " OR ".join(unwrap(f) for f in flt)

        return Subquery(
            sql=f"""
                SELECT {', '.join(
                    fld.full_name_with_alias 
                    for fld in sorted(subquery.fields, key=lambda f: f.alias)
                )}
                FROM ({subquery.sql}) {subquery.alias}
                WHERE {unwrap(filters)}
            """,
            fields=subquery.fields,
            dialect=subquery.dialect,
            alias=subquery.root_alias,
            suffix=subquery.suffix + 1
        )

    return inner


def join(*,
    right_table: IQueryable,
    left_field_alias: FieldDisplayName,
    right_field_alias: FieldDisplayName,
    join_type: str = "inner",
) -> Callable[[IQueryable], Subquery]:
    """Subquery transformation that combines two tables

    :param join_type:         Either 'inner', 'left', 'right' or 'full'.
                              The default join type is 'INNER'
    :param right_table:       Subquery to join to the current (left) table
    :param left_field_alias:  Foreign key on the current (left) table to join to the
                              foreign key on the right table
    :param right_field_alias: Foreign key on the right table to join to the foreign
                              key on the current (left) table
    :return:                  Subquery resulting from the combination of the two tables
    """

    def inner(left_table: IQueryable) -> Subquery:
        jtype = join_type.upper()
        if jtype not in ["INNER", "LEFT", "RIGHT", "FULL"]:
            raise ValueError(f"Invalid join type {join_type!r}")

        left_key = left_table.field(left_field_alias)
        right_key = right_table.field(right_field_alias)

        if jtype == "RIGHT":
            exclude_key = left_key
        else:
            exclude_key = right_key

        fields = [
            fld for fld in chain(left_table.fields, right_table.fields)
            if fld.definition != exclude_key.definition
        ]

        qry = f"""
            SELECT {', '.join(
                fld.full_name_with_alias 
                for fld in sorted(fields, key=lambda f: f.alias)
            )}
            FROM ({left_table.sql}) {left_table.alias}
            {jtype} JOIN ({right_table.sql}) {right_table.alias}
            ON {left_key.definition} = {right_key.definition}
        """

        return Subquery(
            sql=qry,
            fields=fields,
            dialect=left_table.dialect,
            alias=left_table.root_alias,
            suffix=left_table.suffix + 1
        )

    return inner


def order_by(order_by_fields: Dict[FieldDisplayName, SortOrder]) -> Callable[[IQueryable], Subquery]:

    def inner(subquery: IQueryable) -> Subquery:

        order_map = {
            SortOrder.ASCENDING: "{} ASC",
            SortOrder.DESCENDING: "{} DESC"
        }

        order_by_clause = ", ".join(
            order_map[sort_order].format(subquery.field(fld_name).definition)
            for fld_name, sort_order in order_by_fields.items()
        )

        qry = f"""
            SELECT {', '.join(
                fld.full_name_with_alias 
                for fld in sorted(subquery.fields, key=lambda f: f.alias)
            )}
            FROM ({subquery.sql}) {subquery.alias}
            ORDER BY {order_by_clause}
        """

        return Subquery(
            sql=qry,
            fields=subquery.fields,
            dialect=subquery.dialect,
            alias=subquery.root_alias,
            suffix=subquery.suffix + 1
        )

    return inner
