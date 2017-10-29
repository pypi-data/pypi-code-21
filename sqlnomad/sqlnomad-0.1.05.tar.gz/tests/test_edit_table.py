# coding=utf-8

import pytest

from sqlnomad import (
    StorageField,
    StorageTable,
    SqlDialect
)
from sqlnomad.utils import standardize_string


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


def test_add_row_sql(customer_dim):
    new_row = {
        "Customer ID": 1,
        "First Name": "Bill",
        "Last Name": "Murray"
    }
    qry, params = customer_dim.add_row(new_row)
    expected = """
        INSERT INTO [customer_dim] ([first_name], [last_name])
        VALUES (?, ?)
    """
    assert standardize_string(qry) == standardize_string(expected)
    assert params == ("Bill", "Murray")


def test_delete_row_sql(customer_dim):
    qry = customer_dim.delete_row(3)
    assert standardize_string(qry[0]), qry[1] == ("DELETE FROM [customer_dim] WHERE [id] = ?", 3)


def test_update_row_sql(customer_dim):
    new_row = {
        "First Name": "Winston",
        "Last Name": "Churchill"
    }
    qry, params = customer_dim.update_row(primary_key_value=1, row=new_row)
    assert standardize_string(qry) == standardize_string("""
        UPDATE [customer_dim] 
        SET [first_name] = ?, [last_name] = ? 
        WHERE [id] = ?
    """)
    assert params == ("Winston", "Churchill", 1)