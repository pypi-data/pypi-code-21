# -*- coding: utf-8 -*-

"""Test cases for utility functions"""
from __future__ import absolute_import
from builtins import str

import pytest
import os
import errno
import os.path as op
import stat
import flotsam.file_util as sut
from flotsam.pytest_util import unique_filename

_ = unique_filename


@pytest.fixture()
def existent_empty_file(tmpdir):
    filename = op.join(str(tmpdir), 'file_1.txt')
    with open(filename, 'w'):
        pass
    return filename


def test_ensure_dir_new(unique_filename, tmpdir):
    path = str(tmpdir) + unique_filename
    assert not op.exists(path)
    sut.ensure_dir(path)
    assert op.exists(path)
    assert os.stat(path).st_mode & stat.S_IRWXU == stat.S_IRWXU


@pytest.mark.parametrize('mode',
                         [0,
                          stat.S_IRUSR,
                          stat.S_IWUSR,
                          stat.S_IXUSR])
def test_ensure_dir_missing_perm(mode, unique_filename, tmpdir):
    path = str(tmpdir) + unique_filename
    assert not op.exists(path)
    os.mkdir(path)
    assert op.exists(path)
    os.chmod(path, mode)
    try:
        sut.ensure_dir(path)
    except IOError as e:
        assert e.errno == errno.EPERM
    else:
        assert False, 'Should have raised IOError'
    assert op.exists(path)


def test_ensure_dir_existing(unique_filename, tmpdir):
    path = str(tmpdir) + unique_filename
    assert not op.exists(path)
    os.mkdir(path)
    assert op.exists(path)
    sut.ensure_dir(path)
    assert op.exists(path)


def test_ensure_del_missing_file(tmpdir):
    filename = op.join(str(tmpdir), '__NONEXISTANT')
    sut.ensure_deleted(filename)
    assert not op.exists(filename)


def test_ensure_del_missing_dir(tmpdir):
    dirname = str(tmpdir)
    sut.ensure_deleted(dirname)
    assert not op.exists(dirname)


def test_ensure_del_ex_file(existent_empty_file):
    sut.ensure_deleted(existent_empty_file)


def test_ensure_del_ex_dir(tmpdir):
    sut.ensure_deleted(str(tmpdir))
