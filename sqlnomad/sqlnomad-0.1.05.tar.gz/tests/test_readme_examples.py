# coding=utf-8
import pytest

from sqlnomad import *
from sqlnomad import AggregationMethod, SortOrder
from sqlnomad.custom_types import FieldDataType
from sqlnomad.utils import standardize_string
from sqlnomad.subquery import Subquery


@pytest.fixture
def whales():
    sql = """
        SELECT c.id AS [Customer ID]
        FROM dim.customer AS c
        JOIN fact.sales AS s
          ON c.id = s.customer_id
        GROUP BY c.id
        HAVING SUM(sales_amount) >= 10000
    """
    return Subquery(
        sql=sql,
        fields=[SqlField(alias="Customer ID", definition="Customer ID")],
        dialect=SqlDialect.MSSQL,
        alias="Whales"
    )


@pytest.fixture
def customers():
    return StorageTable(
        storage_name="customer",
        display_name="Customers",
        fields=[
            StorageField(storage_name="id", display_name="Customer ID", data_type=FieldDataType.INTEGER),
            StorageField(storage_name="first_name", display_name="First Name", data_type=FieldDataType.STRING),
            StorageField(storage_name="last_name", display_name="Last Name", data_type=FieldDataType.STRING)
        ],
        dialect=SqlDialect.MSSQL,
        schema="dim"
    )


@pytest.fixture
def sales():
    return StorageTable(
        storage_name="sales",
        display_name="Sales",
        fields=[
            StorageField(storage_name="id", display_name="Sales ID", data_type=FieldDataType.INTEGER),
            StorageField(storage_name="customer_id", display_name="Customer ID", data_type=FieldDataType.INTEGER),
            StorageField(storage_name="sales_date", display_name="Sales Date", data_type=FieldDataType.DATE),
            StorageField(storage_name="sales_amount", display_name="Sales Amount", data_type=FieldDataType.FLOAT)
        ],
        dialect=SqlDialect.MSSQL,
        schema="fact"
    )


@pytest.fixture
def transactions(customers, sales):
    return Query(customers).bind(
        join(
            right_table=sales,
            left_field_alias="Customer ID",
            right_field_alias="Customer ID"
        )
    )

def test_combine_storage_tables(transactions):
    actual = standardize_string(transactions.sql)
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
            FROM [dim].[customer]
        ) [Customers]
        INNER JOIN (SELECT [id] AS [Sales ID], [customer_id] AS [Customer ID], [sales_date] AS [Sales Date], [sales_amount] AS [Sales Amount] FROM [fact].[sales]) [Sales]
        ON [Customers].[Customer ID] = [Sales].[Customer ID]
    """)
    assert actual == expected


def test_aggregation_and_order_by(transactions):
    total_sales = transactions.bind(
        aggregate(
            group_by_fields=["First Name", "Last Name"],
            aggregations={"Sales Amount": AggregationMethod.SUM}
        )
    ).bind(order_by({"Sales Amount": SortOrder.DESCENDING}))
    actual = standardize_string(total_sales.sql)
    expected = standardize_string("""
      SELECT [Customers 3].[First Name] AS [First Name], 
             [Customers 3].[Last Name] AS [Last Name], 
             [Customers 3].[Sales Amount] AS [Sales Amount]
      FROM (
          SELECT [Customers 2].[First Name] AS [First Name], 
                 [Customers 2].[Last Name] AS [Last Name], 
                 SUM([Customers 2].[Sales Amount]) AS [Sales Amount] 
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
                  FROM [dim].[customer]
              ) [Customers]
              INNER JOIN (
                  SELECT [id] AS [Sales ID], 
                         [customer_id] AS [Customer ID], 
                         [sales_date] AS [Sales Date], 
                         [sales_amount] AS [Sales Amount] 
                  FROM [fact].[sales]
              ) [Sales]
              ON [Customers].[Customer ID] = [Sales].[Customer ID]
          ) [Customers 2] 
          GROUP BY [Customers 2].[First Name], 
                   [Customers 2].[Last Name]
      ) [Customers 3]
      ORDER BY [Customers 3].[Sales Amount] DESC
    """)
    assert actual == expected


def test_combine_storage_table_with_raw_sql(whales, transactions):
    qry = Query(whales).bind(
        join(
            right_table=transactions,
            left_field_alias="Customer ID",
            right_field_alias="Customer ID"
        )
    )
    actual = standardize_string(qry.sql)
    expected = standardize_string("""
        SELECT [Whales 1].[Customer ID] AS [Customer ID], 
               [Customers 2].[First Name] AS [First Name], 
               [Customers 2].[Last Name] AS [Last Name], 
               [Customers 2].[Sales Amount] AS [Sales Amount], 
               [Customers 2].[Sales Date] AS [Sales Date], 
               [Customers 2].[Sales ID] AS [Sales ID]
        FROM (
            SELECT c.id AS [Customer ID]
            FROM dim.customer AS c
            JOIN fact.sales AS s
              ON c.id = s.customer_id
            GROUP BY c.id
            HAVING SUM(sales_amount) >= 10000
        ) [Whales 1]
        INNER JOIN (
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
                FROM [dim].[customer]
            ) [Customers]
            INNER JOIN (SELECT [id] AS [Sales ID], [customer_id] AS [Customer ID], [sales_date] AS [Sales Date], [sales_amount] AS [Sales Amount] FROM [fact].[sales]) [Sales]
            ON [Customers].[Customer ID] = [Sales].[Customer ID]
        ) [Customers 2]
            ON [Whales 1].[Customer ID] = [Customers 2].[Customer ID]
    """)
    assert actual == expected


if __name__ == "__main__":
    import doctest
    doctest.testmod()