#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `db2table` package."""

import html5lib
import os
from sqlalchemy import create_engine
from html5lib.html5parser import ParseError
import pytest

from click.testing import CliRunner

import db2table
from db2table import cli


def init_db(engine):
    sql_table_1 = '''
    create table test1
    (
        id INT,
        firstname varchar(100),
        lastname varchar(100),
        address varchar(100),
        city varchar(100)
    )
    '''
    sql_table_2 = '''
    create table test2
    (
        id INT,
        firstname varchar(100),
        lastname varchar(100),
        address varchar(100),
        city varchar(100)
    )
    '''

    sql_insert_1 = '''
    INSERT into test1
    VALUES
        (1,"Conan","Smith","55 Rue du Faubourg Saint-Honoré","Paris"),
        (2,"John","Smith","92 Avenue de Wagram","Paris"),
        (3,"San","Smith","22 Avenue de Wagram","Paris")
    '''
    sql_insert_2 = '''
    INSERT into test2
    VALUES
        (1,"Zorro","Smith","55 Rue du Faubourg Saint-Honoré","Paris"),
        (2,"Luffy","Smith","92 Avenue de Wagram","Paris"),
        (3,"Sanji","Smith","22 Avenue de Wagram","Paris")
    '''
    connection = engine.connect()
    connection.execute(sql_table_1)
    connection.execute(sql_insert_1)
    connection.execute(sql_table_2)
    connection.execute(sql_insert_2)
    connection.close()


@pytest.fixture
def db():
    engine = create_engine('sqlite:///')
    init_db(engine)
    return engine


def test_shape_of_table(db):
    data = db2table.to_dict(db)
    assert data != {}
    assert len(data) == 2
    assert len(data['test1'][0].keys()) == 5


def test_to_html5_compliant():
    dummy = [{'a': 1, 'b': 2, 'c': 3}, {'a': 4, 'b': 5, 'c': 6}]
    html = db2table.to_html(dummy, 'test')
    parser = html5lib.HTMLParser(strict=True)
    try:
        parser.parse(html)
        assert True
    except ParseError as e:
        print(e)
        assert False


def test_command_line_interface(tmpdir):
    """Test the CLI."""
    # user enter a path to sqlite db,and output folder
    folder = str(tmpdir.mkdir("html"))
    db_path = str(tmpdir.mkdir("db").join('test.db'))
    engine = create_engine('sqlite:///' + db_path)
    init_db(engine)
    # produce tablename.html for all table in the db
    runner = CliRunner()
    result = runner.invoke(cli, [db_path, folder])
    assert result.exit_code == 0
    len(os.listdir(folder)) == 2
