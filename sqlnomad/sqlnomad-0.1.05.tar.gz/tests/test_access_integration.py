# coding=utf-8
import os
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


@pytest.fixture
def connection():
    path = os.path.abspath("bookstore.mdb")
    connection_string = r"DRIVER={Microsoft Access Driver (*.mdb)};DBQ=" + path + ";"
    return pyodbc.connect(connection_string)


@pytest.fixture
def sales_fact():
    return StorageTable(
        storage_name="sales_fact",
        display_name="Sales",
        fields=[
            StorageField(storage_name="id", display_name="Sales ID"),
            StorageField(storage_name="customer_id", display_name="Customer ID"),
            StorageField(storage_name="sales_date", display_name="Sales Date"),
            StorageField(storage_name="sales_amount", display_name="Sales Amount")
        ],
        dialect=SqlDialect.ACCESS
    )

@pytest.fixture
def customer_dim():
    return StorageTable(
        storage_name="customer_dim",
        display_name="Customers",
        fields=[
            StorageField(storage_name="id", display_name="Customer ID"),
            StorageField(storage_name="first_name", display_name="First Name"),
            StorageField(storage_name="last_name", display_name="Last Name")
        ],
        dialect=SqlDialect.ACCESS
    )


def test_access_driver_available():
    assert [d for d in pyodbc.drivers() if d.startswith('Microsoft Access Driver')]


def test_order_columns(customer_dim, connection):
    qry = Query(customer_dim).bind(order_columns(["Last Name", "First Name"]))
    rows = connection.execute(qry.sql).fetchone()
    assert str(rows) == "('Stefanovic', 'Mark')"


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
