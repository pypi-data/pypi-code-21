# coding=utf-8

import pyodbc

import pytest

from sqlnomad import (
    StorageTable,
    StorageField,
    SqlDialect,
    Query,
    join,
    find,
    SqlFilter,
    FilterOperator
)
from sqlnomad.query_transformations import order_columns

_SCHEMA = """
    USE Bookstore;
    
    CREATE TABLE dim.customer (
        id INT IDENTITY(1, 1)
        , first_name VARCHAR(80)
        , last_name VARCHAR(80)
    );
    
    CREATE TABLE fact.sales (
        id INT IDENTITY(1, 1)
        , customer_id INT
        , product_id INT
        , sales_date DATE
        , sales_amount DECIMAL(19, 2)
    );
    
    INSERT INTO dim.customer (first_name, last_name)
        VALUES ('Mark', 'Stefanovic');
    INSERT INTO dim.customer(first_name, last_name)
        VALUES ('Adam', 'Smith');
    
    INSERT INTO fact.sales (customer_id, product_id, sales_date, sales_amount) 
        VALUES (1, 3, '2016-01-03', 13.09);
    INSERT INTO fact.sales (customer_id, product_id, sales_date, sales_amount) 
        VALUES (2, 7, '2014-02-21', 4.24);
    INSERT INTO fact.sales (customer_id, product_id, sales_date, sales_amount)
        VALUES (2, 1, '2011-09-04', 5.18);
    INSERT INTO fact.sales (customer_id, product_id, sales_date, sales_amount) 
        VALUES (1, 3, '2017-03-03', 7.29);
    INSERT INTO fact.sales (customer_id, product_id, sales_date, sales_amount) 
        VALUES (4, 2, '2015-06-07', 9.24);
"""


@pytest.fixture
def connection():
    return pyodbc.connect(
        Trusted_Connection='yes',
        driver='{SQL Server}',
        server='localhost\SQLEXPRESS',
        database='Bookstore'
    )


@pytest.fixture
def sales_fact():
    return StorageTable(
        storage_name="sales",
        display_name="Sales",
        fields=[
            StorageField(storage_name="id", display_name="Sales ID"),
            StorageField(storage_name="customer_id", display_name="Customer ID"),
            StorageField(storage_name="sales_date", display_name="Sales Date"),
            StorageField(storage_name="sales_amount", display_name="Sales Amount")
        ],
        dialect=SqlDialect.MSSQL,
        schema="fact"
    )


@pytest.fixture
def customer_dim():
    return StorageTable(
        storage_name="customer",
        display_name="Customers",
        fields=[
            StorageField(storage_name="id", display_name="Customer ID"),
            StorageField(storage_name="first_name", display_name="First Name"),
            StorageField(storage_name="last_name", display_name="Last Name")
        ],
        dialect=SqlDialect.MSSQL,
        schema="dim"
    )


def test_sql_server_driver_available():
    assert [d for d in pyodbc.drivers() if d.startswith('SQL Server')]


def test_join(customer_dim, sales_fact, connection):
    qry = Query(customer_dim).bind(
        join(
            right_table=sales_fact,
            left_field_alias="Customer ID",
            right_field_alias="Customer ID"
        )
    ).bind(
        find([
            SqlFilter(field_alias="First Name", operator=FilterOperator.EQUALS, value="Mark"),
            SqlFilter(field_alias="Last Name", operator=FilterOperator.EQUALS, value="Stefanovic")
        ])
    )

    cursor = connection.cursor()
    cursor.execute(qry.sql)
    row = cursor.fetchone()
    assert (row[1], row[2]) == ("Mark", "Stefanovic")


def test_order_columns(connection, customer_dim):
    qry = Query(customer_dim).bind(order_columns(["Last Name", "First Name"]))
    rows = connection.execute(qry.sql).fetchone()
    assert str(rows) == "('Stefanovic', 'Mark')"