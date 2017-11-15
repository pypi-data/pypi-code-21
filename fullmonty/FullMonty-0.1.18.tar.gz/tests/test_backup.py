# coding=utf-8

"""
Tests the backup functionality used when rendering templates.
"""

import os

from fullmonty.backup import backup_filename, next_backup_filename


def test_backup_filename():
    """Test getting the backup file name for a given file name"""
    assert backup_filename('foo') == 'foo~'
    assert backup_filename('foo~') == 'foo~'
    assert backup_filename('foo1~') == 'foo1~'


def test_next_backup_filename():
    """Test generating the next backup file name"""
    assert next_backup_filename('foo', ['a', 'b']) == 'foo~'
    assert next_backup_filename('foo', ['a', 'b', 'foo']) == 'foo~'
    assert next_backup_filename('foo', ['a', 'b', 'foo~']) == 'foo1~'
    assert next_backup_filename('foo', ['a', 'b', 'foo', 'foo~']) == 'foo1~'
    assert next_backup_filename('foo', ['a', 'b', 'foo~', 'foo1~']) == 'foo2~'
    assert next_backup_filename('foo', ['a', 'b', 'foo~', 'foo1~', 'foo3~']) == 'foo4~'
    assert next_backup_filename('foo', ['a', 'b', 'foo', 'foo1~', 'foo3~']) == 'foo~'


def backup_files(dest_dir):
    """
    :param dest_dir: the directory where the backup files should be located
    :returns: a generator for all of the backup files in the dest_dir
    """
    return [file_ for file_ in os.listdir(dest_dir) if file_.endswith('~')]
