# coding=utf-8

import pytest

from sqlnomad import (
    AggregationMethod,
    FilterOperator,
    SortOrder,
    SqlDialect,
    SqlFilter,
    Query,
    aggregate,
    find,
    join,
    order_by,
    StorageTable,
    StorageField
)
from sqlnomad.custom_types import FieldDataType
from sqlnomad.query_transformations import order_columns
from sqlnomad.utils import standardize_string


@pytest.fixture
def sales_fact():
    return StorageTable(
        storage_name="sales_fact",
        display_name="Sales",
        fields=[
            StorageField(
                storage_name="id",
                display_name="Sales ID",
                data_type=FieldDataType.INTEGER
            ),
            StorageField(
                storage_name="customer_id",
                display_name="Customer ID",
                data_type=FieldDataType.INTEGER
            ),
            StorageField(
                storage_name="sales_date",
                display_name="Sales Date",
                data_type=FieldDataType.DATE
            ),
            StorageField(
                storage_name="sales_amount",
                display_name="Sales Amount",
                data_type=FieldDataType.FLOAT
            )
        ],
        dialect=SqlDialect.MSSQL,
        schema="fact"
    )


@pytest.fixture
def customer_dim():
    return StorageTable(
        storage_name="customer_dim",
        display_name="Customers",
        fields=[
            StorageField(
                storage_name="id",
                display_name="Customer ID",
                data_type=FieldDataType.INTEGER
            ),
            StorageField(
                storage_name="first_name",
                display_name="First Name",
                data_type=FieldDataType.STRING
            ),
            StorageField(
                storage_name="last_name",
                display_name="Last Name",
                data_type=FieldDataType.STRING
            )
        ],
        dialect=SqlDialect.MSSQL,
        schema="dim"
    )

@pytest.fixture
def filters():
    return [
        [
            SqlFilter(field_alias="First Name", operator=FilterOperator.EQUALS, value="Mark"),
            SqlFilter(field_alias="Last Name", operator=FilterOperator.EQUALS, value="Stefanovic")
        ],
        [SqlFilter(field_alias="Sales Amount", operator=FilterOperator.GREATER_THAN, value=0)]
    ]


def test_storage_table_sql(customer_dim):
    actual = standardize_string(customer_dim.sql)
    expected = standardize_string("""
        SELECT [id] AS [Customer ID], 
               [first_name] AS [First Name], 
               [last_name] AS [Last Name] 
        FROM [dim].[customer_dim]
    """)
    assert actual == expected


def test_aggregate_query(sales_fact):
    qry = Query(sales_fact).bind(
        aggregate(
            group_by_fields=["Sales Date"],
            aggregations={
                "Sales Amount": AggregationMethod.SUM,
                "Sales ID": AggregationMethod.COUNT
            }
        )
    )
    actual = standardize_string(qry.sql)
    expected = standardize_string("""
        SELECT SUM([Sales].[Sales Amount]) AS [Sales Amount], 
               [Sales].[Sales Date] AS [Sales Date],
               COUNT([Sales].[Sales ID]) AS [Sales ID]
        FROM (
            SELECT [id] AS [Sales ID], 
                   [customer_id] AS [Customer ID], 
                   [sales_date] AS [Sales Date], 
                   [sales_amount] AS [Sales Amount]
            FROM [fact].[sales_fact]
        ) [Sales] 
        GROUP BY [Sales].[Sales Date]
    """)
    assert actual == expected


def test_find(customer_dim):
    flts = [
        [
            SqlFilter(field_alias="First Name", operator=FilterOperator.EQUALS, value="Mark"),
            SqlFilter(field_alias="Last Name", operator=FilterOperator.EQUALS, value="Stefanovic")
        ], [SqlFilter(field_alias="Last Name", operator=FilterOperator.EQUALS, value="Smith")]
    ]

    qry = Query(customer_dim).bind(find(flts))
    actual = standardize_string(qry.sql)
    expected = standardize_string("""
        SELECT [Customers].[Customer ID] AS [Customer ID], 
               [Customers].[First Name] AS [First Name], 
               [Customers].[Last Name] AS [Last Name] 
        FROM (
            SELECT [id] AS [Customer ID], 
                   [first_name] AS [First Name], 
                   [last_name] AS [Last Name] 
            FROM [dim].[customer_dim]
            ) [Customers] 
        WHERE 
            (
                [Customers].[First Name] = 'Mark' 
                AND [Customers].[Last Name] = 'Stefanovic'
            ) 
            OR ([Customers].[Last Name] = 'Smith')
    """)
    assert actual == expected


def test_join(customer_dim, sales_fact):
    qry = Query(customer_dim).bind(
        join(
            right_table=sales_fact,
            left_field_alias="Customer ID",
            right_field_alias="Customer ID"
        )
    )
    actual = standardize_string(qry.sql)
    expected = standardize_string("""
      SELECT [Customers].[Customer ID] AS [Customer ID], 
             [Customers].[First Name] AS [First Name], 
             [Customers].[Last Name] AS [Last Name], 
             [Sales].[Sales Amount] AS [Sales Amount], 
             [Sales].[Sales Date] AS [Sales Date], 
             [Sales].[Sales ID] AS [Sales ID] 
      FROM (
          SELECT [id] AS [Customer ID], 
                 [first_name] AS [First Name], 
                 [last_name] AS [Last Name] 
          FROM [dim].[customer_dim]
      ) [Customers] 
      INNER JOIN (
          SELECT [id] AS [Sales ID], 
                 [customer_id] AS [Customer ID], 
                 [sales_date] AS [Sales Date], 
                 [sales_amount] AS [Sales Amount] 
          FROM [fact].[sales_fact]
      ) [Sales] 
      ON [Customers].[Customer ID] = [Sales].[Customer ID]
    """)
    assert actual == expected


def test_composition(customer_dim, sales_fact):
    filters = [
        [
            SqlFilter(field_alias="First Name", operator=FilterOperator.EQUALS, value="Mark"),
            SqlFilter(field_alias="Last Name", operator=FilterOperator.EQUALS, value="Stefanovic")
        ], [SqlFilter(field_alias="Sales Amount", operator=FilterOperator.GREATER_THAN, value=0)]
    ]
    qry = Query(customer_dim).bind(
        join(
            join_type="left",
            right_table=sales_fact,
            left_field_alias="Customer ID",
            right_field_alias="Customer ID"
        )
    ).bind(find(filters))

    actual = standardize_string(qry.sql)
    expected = standardize_string("""
      SELECT [Customers 2].[Customer ID] AS [Customer ID], 
             [Customers 2].[First Name] AS [First Name], 
             [Customers 2].[Last Name] AS [Last Name], 
             [Customers 2].[Sales Amount] AS [Sales Amount], 
             [Customers 2].[Sales Date] AS [Sales Date], 
             [Customers 2].[Sales ID] AS [Sales ID] 
      FROM (
          SELECT [Customers].[Customer ID] AS [Customer ID], 
                 [Customers].[First Name] AS [First Name], 
                 [Customers].[Last Name] AS [Last Name], 
                 [Sales].[Sales Amount] AS [Sales Amount], 
                 [Sales].[Sales Date] AS [Sales Date], 
                 [Sales].[Sales ID] AS [Sales ID] 
          FROM (
              SELECT [id] AS [Customer ID], 
                     [first_name] AS [First Name], 
                     [last_name] AS [Last Name] 
              FROM [dim].[customer_dim]
          ) [Customers] 
          LEFT JOIN (
              SELECT [id] AS [Sales ID], [customer_id] AS [Customer ID], 
                     [sales_date] AS [Sales Date], 
                     [sales_amount] AS [Sales Amount] 
              FROM [fact].[sales_fact]
          ) [Sales] 
              ON [Customers].[Customer ID] = [Sales].[Customer ID]) [Customers 2] 
          WHERE (
              [Customers 2].[First Name] = 'Mark' 
              AND [Customers 2].[Last Name] = 'Stefanovic'
          ) OR ([Customers 2].[Sales Amount] > '0')
    """)
    assert actual == expected


def test_order_by(customer_dim):
    qry = Query(customer_dim).bind(
        order_by({
            "First Name": SortOrder.ASCENDING,
            "Last Name": SortOrder.DESCENDING
        })
    )
    actual = standardize_string(qry.sql)
    expected = standardize_string("""
        SELECT [Customers].[Customer ID] AS [Customer ID], 
               [Customers].[First Name] AS [First Name], 
               [Customers].[Last Name] AS [Last Name] 
        FROM (
            SELECT [id] AS [Customer ID], 
                   [first_name] AS [First Name], 
                   [last_name] AS [Last Name] 
            FROM [dim].[customer_dim]
        ) [Customers] 
        ORDER BY [Customers].[First Name] ASC, 
                 [Customers].[Last Name] DESC
    """)
    assert actual == expected


def test_order_columns(customer_dim):
    qry = Query(customer_dim).bind(order_columns(field_aliases=["Last Name", "First Name"]))
    actual = standardize_string(qry.sql)
    expected = standardize_string(f"""
      SELECT [Customers].[Last Name] AS [Last Name], 
             [Customers].[First Name] AS [First Name] 
      FROM (
          SELECT [id] AS [Customer ID], 
                 [first_name] AS [First Name], 
                 [last_name] AS [Last Name] 
          FROM [dim].[customer_dim]
      ) [Customers]
    """)
    assert actual == expected

