#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
py.test configuration.

Widely-used test fixtures.
"""

import pytest

BINARY_DATA = b'10011001'


@pytest.fixture
def binary_file(tmpdir):
    """Fixture to produce a binary file on disk."""
    filename = tmpdir.join('blob.bin').ensure().strpath
    with open(filename, 'wb') as output_file:
        output_file.write(BINARY_DATA)
    return filename
