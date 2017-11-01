#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `wkr.os` package."""

import os
import random
import string

import pytest

from wkr.os import (backup_file, mkdir_p, momentary_chdir, open_atomic,
                    temp_file_name, write_atomic)


def test_mkdir_p_single(tmpdir):
    """Test mkdir_p on creating a single directory."""
    path = tmpdir.join('newdir')
    assert not path.exists()
    mkdir_p(path.strpath)
    assert path.exists()


def test_mkdir_p_double(tmpdir):
    """Test mkdir_p on creating two directories."""
    path1 = tmpdir.join('newdir2')
    assert not path1.exists()
    path2 = path1.join('subdir')
    assert not path2.exists()
    mkdir_p(path2.strpath)
    assert path1.exists()
    assert path2.exists()


def test_mkdir_p_exists(tmpdir):
    """Test mkdir_p on creating a directory that already exists."""
    path = tmpdir.join('newdir').ensure(dir=True)
    assert path.exists()
    assert path.isdir()
    mkdir_p(path.strpath)  # should not throw an exception


def test_mkdir_p_file_exists(tmpdir):
    """Test mkdir_p creating a directory that exists as a file."""
    path = tmpdir.join('newfile').ensure(dir=False)
    assert path.exists()
    assert not path.isdir()
    with pytest.raises(OSError):
        mkdir_p(path.strpath)  # should throw an exception


@pytest.fixture(params=['none', 'random'])
def tmpdir_suffix(request):
    """Fixture to produce random 3-character suffix values."""
    if request.param == 'none':
        return ''
    elif request.param == 'random':
        # random suffix
        rsuffix = '.' + ''.join([random.choice(string.ascii_letters)
                                 for _ in range(3)])
        return rsuffix
    else:
        return ''


def test_temp_file_name(tmpdir, tmpdir_suffix):
    """Basic test of wkr.os.temp_file_name."""
    # directory is empty
    assert not tmpdir.listdir()
    with temp_file_name(suffix=tmpdir_suffix,
                        directory=tmpdir.strpath) as newpath:
        assert newpath.endswith(tmpdir_suffix)
        # either the directory is empty and the file is not there, or
        # it is there and the directory is not empty, but the file is
        # empty
        assert ((not tmpdir.listdir() and not os.path.exists(newpath)) or (
            tmpdir.listdir() and
            os.path.exists(newpath) and
            not os.stat(newpath).st_size))
        # we should be able to write to the file
        output_file = open(newpath, 'wb')
        output_file.write(b'abcde')
        output_file.close()
        # now the file should be there
        assert tmpdir.listdir()
        assert os.path.exists(newpath)
        assert os.stat(newpath).st_size > 0
    # directory is empty
    assert not tmpdir.listdir()


def test_temp_file_name_delete(tmpdir):
    """Test wkr.os.temp_file_name where we manually delete the tmpfile."""
    with temp_file_name(directory=tmpdir.strpath) as newpath:
        # write to the file
        with open(newpath, 'wb') as output_file:
            output_file.write(b'abcde')
        # delete the file
        os.remove(newpath)
    # should not raise an exception


def test_open_atomic(tmpdir, binary_file):
    """Test wkr.os.open_atomic."""
    binary_path = tmpdir.__class__(binary_file)
    assert tmpdir.exists()
    assert binary_path.exists()
    assert binary_path.size() > 0
    original_contents = binary_path.read(mode='rb')
    # now we do an atomic write on binary_file
    with open_atomic(binary_file, fsync=True) as output_file:
        new_contents = b'abcde'
        assert new_contents != original_contents
        output_file.write(new_contents)
        output_file.flush()
        # at this point the original file still hasn't changed
        assert binary_path.read(mode='rb') == original_contents
    # now we close the file, and it's atomically moved into its final
    # location
    assert binary_path.read(mode='rb') == new_contents


def test_backup_file(tmpdir, binary_file):
    """Test wkr.os.backup_file."""
    binary_path = tmpdir.__class__(binary_file)
    assert tmpdir.exists()
    assert binary_path.exists()
    assert binary_path.size()
    original_contents = binary_path.read(mode='rb')
    # backup file
    backup_path = binary_path.new(basename=binary_path.basename + '~')
    assert not backup_path.exists()
    # now do the backup
    backup_file(binary_file)
    # assert that the backup_path exists and that it contains the same
    # content as the original file
    assert binary_path.exists()
    assert binary_path.read(mode='rb') == original_contents
    assert backup_path.exists()
    assert backup_path.read(mode='rb') == original_contents


def test_backup_file_exists(tmpdir, binary_file):
    """Test wkr.os.backup_file where the backup file already exists."""
    binary_path = tmpdir.__class__(binary_file)
    # create the backup file and put something in it
    backup_path = binary_path.new(basename=binary_path.basename + '~')
    original_contents = b'abcde'
    backup_path.ensure().write(original_contents)
    # now do the backup
    backup_file(binary_file)
    # assert that the backup_path exists and that it contains the same
    # content as the original file
    assert backup_path.read(mode='rb') != original_contents
    assert backup_path.read(mode='rb') == binary_path.read(mode='rb')


def test_write_atomic(tmpdir, binary_file):
    """Test wkr.os.write_atomic."""
    binary_path = tmpdir.__class__(binary_file)
    assert tmpdir.exists()
    assert binary_path.exists()
    assert binary_path.size() > 0
    original_contents = binary_path.read(mode='rb')
    # backup file
    backup_path = binary_path.new(basename=binary_path.basename + '~')
    assert not backup_path.exists()
    # now do the atomic write
    new_contents = b'abcde'
    assert new_contents != original_contents
    write_atomic([new_contents], binary_file)
    # assert that the backup_path exists and that it contains the same
    # content as the original file
    assert backup_path.exists()
    assert backup_path.read(mode='rb') == original_contents
    # assert that the original file exists, with different contents
    assert binary_path.exists()
    assert binary_path.read(mode='rb') == new_contents


def test_momentary_chdir(tmpdir):
    """Test wkr.os.momentary_chdir."""
    start_dir = os.getcwd()
    with momentary_chdir(tmpdir.strpath):
        new_dir = os.getcwd()
        assert new_dir != start_dir
        assert new_dir == tmpdir.strpath
    assert os.getcwd() == start_dir


def test_momentary_chdir_fail(tmpdir):
    """Test wkr.os.momentary_chdir."""
    start_dir = os.getcwd()
    path = tmpdir.join('newdir')
    assert not path.exists()
    with pytest.raises(OSError):
        with momentary_chdir(path.strpath):
            # this is never executed
            assert False
    assert os.getcwd() == start_dir
