#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `wkr.io` package."""

import gzip
import itertools
import os
import random
import re
import sys
import zipfile
from collections import Counter

import pytest

import wkr
import wkr.io
from wkr.compat import PY2, binary_type, chr, text_type

from .conftest import BINARY_DATA

try:
    import lzma
except ImportError:
    import backports.lzma as lzma


if PY2:
    try:
        import cStringIO
        BytesIO = cStringIO.StringIO
    except ImportError:
        import StringIO
        BytesIO = StringIO.StringIO
else:
    from io import BytesIO as BytesIO


# some printable unicode characters
WORD_CHARS = [chr(x) for x in (list(range(0x21, 0x7f)) +
                               list(range(0xa1, 0xad)) +
                               list(range(0xae, 0x100)))]


@pytest.fixture
def random_lines():
    """Fixture to produce random unicode text."""
    lines = []
    for _ in range(random.randint(12, 24)):
        line = []
        for _ in range(random.randint(5, 13)):
            word = u''.join([random.choice(WORD_CHARS)
                             for _ in range(random.randint(3, 8))])
            line.append(word)
        line = u' '.join(line)
        lines.append(line)
    return lines


@pytest.fixture(params=['latin-1', 'utf-8',
                        'utf-16', 'utf-16le', 'utf-16be',
                        'utf-32', 'utf-32le', 'utf-32be'])
def text_file(tmpdir, random_lines, request):
    """Fixture to produce a random text file."""
    encoding = request.param
    filename = tmpdir.join('text.{}.txt'.format(encoding)).ensure().strpath
    with open(filename, 'wb') as output_file:
        output_file.write((u'\n'.join(random_lines) + u'\n').encode(encoding))
    return filename


@pytest.fixture(params=[('bin', open),
                        ('xz', lzma.LZMAFile),
                        ('gz', gzip.open)])
def compressed_file(tmpdir, request):
    """Fixture to produce compressed files."""
    ext, open_fn = request.param
    path = tmpdir.join('test.{}'.format(ext)).ensure().strpath
    with open_fn(path, 'wb') as output_file:
        output_file.write(BINARY_DATA)
    return path


@pytest.fixture
def zip_file(tmpdir):
    """Fixture to produce a zip file."""
    filename = tmpdir.join('test.zip').ensure().strpath
    with zipfile.ZipFile(filename, 'w') as archive:
        for num in range(1, 4):
            contents = u'line {}'.format(num).encode('ascii')
            contents += b'\n' + BINARY_DATA
            archive.writestr('file{}.txt'.format(num), contents)
    return filename


def test_open_finds_streams():
    """Test that wkr.open returns standard streams."""
    assert wkr.open('-', 'r') is sys.stdin
    assert wkr.open('-', 'rb') is sys.stdin
    assert wkr.open('-', 'w') is sys.stdout
    assert wkr.open('-', 'wb') is sys.stdout
    assert wkr.open('-', 'a') is sys.stdout
    assert wkr.open('-', 'ab') is sys.stdout


def test_read_compressed_file(compressed_file):
    """Test that wkr.open can read compressed file formats."""
    with wkr.open(compressed_file, 'rb') as input_file:
        data = input_file.read()
        assert isinstance(data, binary_type)
        assert data == BINARY_DATA


def test_already_open_file(binary_file):
    """Test that wkr.open passes through files that are already open."""
    with open(binary_file, 'rb') as input_file:
        for mode in ['r', 'a', 'w', 'rb', 'ab', 'wb']:
            assert wkr.open(input_file, mode) is input_file


def test_read_zip_file(zip_file):
    """Test that wkr.open can read zip files."""
    for num in range(1, 4):
        with wkr.open('{zip_file}:file{num}.txt'.format(
                zip_file=zip_file, num=num)) as input_file:
            contents = input_file.read()
            assert isinstance(contents, binary_type)
            contents = contents.split(b'\n')
            assert len(contents) == 2
            assert contents[0] == (u'line {}'.format(num)).encode('ascii')
            assert contents[1] == BINARY_DATA


def test_write_compressed_file(compressed_file):
    """Test that wkr.open can write to compressed file formats."""
    contents = b'new file\n' + BINARY_DATA
    with wkr.open(compressed_file, 'wb') as output_file:
        output_file.write(contents)
    ext = os.path.splitext(compressed_file)[1]
    open_fn = {'.bin': open, '.xz': lzma.LZMAFile, '.gz': gzip.open}.get(ext)
    input_file = open_fn(compressed_file, 'rb')
    data = input_file.read()
    assert isinstance(data, binary_type)
    assert data == contents
    input_file.close()


def test_cannot_write_zip_file(zip_file):
    """Test that wkr.open cannot write to zip files."""
    modes = ['w', 'a', 'wb', 'ab']
    for mode in modes:
        with pytest.raises(ValueError):
            _ = wkr.open('{}:file1.txt'.format(zip_file), mode)  # noqa f841


def test_cannot_open_non_files():
    """Test that wkr.open fails if it is passed something bad."""
    modes = ['r', 'rb', 'a', 'ab', 'w', 'wb']
    args = [
        (1,),               # tuple
        1,                  # int
        1.0,                # float
        {'key': 'value'},   # dict
        set(range(10)),     # set
        [1, 2, 3, 4],       # list
    ]
    for (arg, mode) in itertools.product(args, modes):
        with pytest.raises(TypeError):
            _ = wkr.open(arg, mode)  # noqa f841


def test_lines_read(text_file, random_lines):
    """Test the wkr.lines method on reading text files."""
    encoding = re.match(r'.+\.([^.]+)\.txt$', text_file).group(1)
    # read with string decoding
    expected_output = [line + u'\n' for line in random_lines]
    read_lines = list(wkr.lines(text_file, encoding))
    assert all(isinstance(x, text_type) for x in read_lines)
    assert read_lines == expected_output
    # try reading without string decoding
    expected_output = list(
        BytesIO((u'\n'.join(random_lines) + u'\n').encode(encoding)))
    read_lines = list(wkr.lines(text_file, None))
    assert all(isinstance(x, binary_type) for x in read_lines)
    assert read_lines == expected_output


def test_lines_read_compressed(tmpdir, random_lines):
    """Test that wkr.lines can read compressed files."""
    # make a compressed file
    path = tmpdir.join('text.gz').ensure().strpath
    with wkr.open(path, 'wb') as output_file:
        for line in random_lines:
            output_file.write(line.encode('utf-8') + b'\n')
    # now read it back in with wkr.lines()
    loaded_lines = list(wkr.lines(path))
    assert [[line.strip() for line in loaded_lines] == random_lines]


def test_count_lines(tmpdir, random_lines):
    """Test the wkr.count_lines method."""
    for num_lines in range(len(random_lines) + 1):
        filename = tmpdir.join('text.txt')
        assert not filename.exists()
        with open(filename.strpath, 'wb') as output_file:
            output_file.write(
                (u'\n'.join(random_lines[:num_lines]) + u'\n').encode('utf-8'))
        assert filename.exists()
        assert wkr.io.count_lines(filename.strpath) == max(num_lines, 1)
        filename.remove()
        assert not filename.exists()


def test_load_counter(tmpdir):
    """Test the wkr.io.load_counter method."""
    for size in [0, 1, 10, 100, 1000]:
        # produce a Counter dictionary with random counts
        counter = Counter()
        for key in range(size):
            key = 'key{}'.format(key)
            count = random.randint(0, 10000)
            counter[key] = count
        assert len(counter) == size
        # write the counter out to file
        filename = tmpdir.join('counts.tsv').ensure().strpath
        with open(filename, 'wb') as output_file:
            for (key, count) in counter.items():
                output_file.write(
                    u'{}\t{}\n'.format(count, key).encode('utf-8'))
        # read it back in
        assert wkr.io.load_counter(filename) == counter


def test_load_counter_2(tmpdir):
    """Test the wkr.io.load_counter method."""
    # write the counter out to file
    filename = tmpdir.join('counts.tsv').ensure().strpath
    with open(filename, 'wb') as output_file:
        output_file.write(b'2\ta\n')
        output_file.write(b'4\tb\n')
        output_file.write(b'1\tc\n')
        output_file.write(b'3\ta\n')
    # read it back in
    assert wkr.io.load_counter(filename) == Counter('aabbbbcaaa')


def test_load_counter_3(tmpdir):
    """Test the wkr.io.load_counter method."""
    # write the counter out to file
    filename = tmpdir.join('counts.tsv').ensure().strpath
    with open(filename, 'wb') as output_file:
        output_file.write(b'2\ta\tb\n')
        output_file.write(b'4\tb\tb\n')
        output_file.write(b'1\tc\tb\n')
        output_file.write(b'3\ta\ta\n')
    # read it back in
    assert wkr.io.load_counter(filename) == Counter(dict([
        (('a', 'b'), 2),
        (('b', 'b'), 4),
        (('c', 'b'), 1),
        (('a', 'a'), 3),
    ]))
