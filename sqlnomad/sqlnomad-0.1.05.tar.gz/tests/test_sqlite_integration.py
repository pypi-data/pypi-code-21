# coding=utf-8
import sqlite3

import pytest

from sqlnomad import (
    StorageTable,
    StorageField,
    SqlDialect,
    Query,
    find,
    join,
    SqlFilter,
    FilterOperator
)
from sqlnomad.query_transformations import order_columns


@pytest.fixture
def connection():
    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    cur.execute("""
      CREATE TABLE sales_fact (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        sales_date DATETIME,
        sales_amount REAL
      )
    """)
    cur.execute("INSERT INTO sales_fact (id, customer_id, product_id, sales_date, sales_amount) "
                "VALUES (1, 1, 3, '2016-01-03', 13.09)")
    cur.execute("INSERT INTO sales_fact (id, customer_id, product_id, sales_date, sales_amount) "
                "VALUES (2, 2, 7, '2014-02-21', 4.24)")
    cur.execute("INSERT INTO sales_fact (id, customer_id, product_id, sales_date, sales_amount) "
                "VALUES (3, 2, 1, '2011-09-04', 5.18)")
    cur.execute("INSERT INTO sales_fact (id, customer_id, product_id, sales_date, sales_amount) "
                "VALUES (4, 1, 3, '2017-03-03', 7.29)")
    cur.execute("INSERT INTO sales_fact (id, customer_id, product_id, sales_date, sales_amount) "
                "VALUES (5, 4, 2, '2015-06-07', 9.24)")

    cur.execute("""
      CREATE TABLE customer_dim (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT
      )
    """)
    cur.execute("INSERT INTO customer_dim (id, first_name, last_name) "
                "VALUES (1, 'Mark', 'Stefanovic')")
    cur.execute("INSERT INTO customer_dim (id, first_name, last_name) "
                "VALUES (2, 'Adam', 'Smith')")
    con.commit()
    return con


@pytest.fixture
def sales_fact():
    return StorageTable(
        storage_name="sales_fact",
        display_name="Sales",
        fields=[
            StorageField(storage_name="id", display_name="Sales ID"),
            StorageField(storage_name="customer_id",
                         display_name="Customer ID"),
            StorageField(storage_name="sales_date",
                         display_name="Sales Date"),
            StorageField(storage_name="sales_amount",
                         display_name="Sales Amount")
        ],
        dialect=SqlDialect.MSSQL
    )


@pytest.fixture
def customer_dim():
    return StorageTable(
        storage_name="customer_dim",
        display_name="Customers",
        fields=[
            StorageField(storage_name="id", display_name="Customer ID"),
            StorageField(storage_name="first_name",
                         display_name="First Name"),
            StorageField(storage_name="last_name",
                         display_name="Last Name")
        ],
        dialect=SqlDialect.MSSQL,
        primary_key_alias="Customer ID"
    )


def test_join(connection, customer_dim, sales_fact):
    qry = Query(customer_dim).bind(
        join(
            right_table=sales_fact,
            left_field_alias="Customer ID",
            right_field_alias="Customer ID"
        )
    ).bind(
        find([
            SqlFilter(field_alias="First Name",
                      operator=FilterOperator.EQUALS, value="Mark"),
            SqlFilter(field_alias="Last Name",
                      operator=FilterOperator.EQUALS,
                      value="Stefanovic")
        ])
    )

    rows = connection.execute(qry.sql).fetchall()
    assert rows[0] == (1, 'Mark', 'Stefanovic', 13.09, '2016-01-03', 1)


def test_add_row(connection, customer_dim):
    new_row = {
        "Customer ID": 1,
        "First Name": "Bill",
        "Last Name": "Murray"
    }
    qry = customer_dim.add_row(new_row)
    connection.execute(*qry)
    rows = connection.execute("SELECT * FROM customer_dim").fetchall()
    assert rows[-1] == (3, 'Bill', 'Murray')


def test_delete_row(connection, customer_dim):
    qry = customer_dim.delete_row(1)
    connection.execute(*qry)
    rows = connection.execute("SELECT * FROM customer_dim").fetchall()
    assert rows == [(2, 'Adam', 'Smith')]


def test_order_columns(connection, customer_dim):
    qry = Query(customer_dim).bind(order_columns(["Last Name", "First Name"]))
    rows = connection.execute(qry.sql).fetchone()
    assert rows == ('Stefanovic', 'Mark')


def test_update_row(connection, customer_dim):
    new_vals = {
        "First Name": "Winston",
        "Last Name": "Churchill"
    }
    qry = customer_dim.update_row(
        primary_key_value=1,
        row=new_vals
    )
    connection.execute(*qry)
    rows = connection.execute("SELECT * FROM customer_dim").fetchall()
    assert rows == [(1, 'Winston', 'Churchill'), (2, 'Adam', 'Smith')]