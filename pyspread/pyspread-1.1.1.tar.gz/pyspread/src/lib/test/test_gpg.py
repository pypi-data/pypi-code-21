#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------


"""
test_gpg
========

Unit tests for gpg.py

"""

import os
import sys

import pytest

import wx
app = wx.App()

TESTPATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-1]) + os.sep
sys.path.insert(0, TESTPATH)
sys.path.insert(0, TESTPATH + (os.sep + os.pardir) * 3)
sys.path.insert(0, TESTPATH + (os.sep + os.pardir) * 2)

from src.config import config

from src.lib.testlib import params, pytest_generate_tests

try:
    import gnupg
    import src.lib.gpg as gpg
    from src.lib.gpg import genkey, fingerprint2keyid
except ImportError:
    gnupg = None

config_fingerprint = config["gpg_key_fingerprint"]
fingerprint = None


def setup_function(function):
    """Creates a GPG key if necessary"""

    if gnupg is None:
        # gnupg is not installed
        return

    global fingerprint
    if fingerprint2keyid(config["gpg_key_fingerprint"]) is None:
        # No GPG key is configured
        fingerprint = genkey(key_name="pyspread_test_key")
    else:
        # Use preconfigured key
        fingerprint = config_fingerprint


def teardown_module(module):
    """Deletes previously generated GPG key"""

    if gnupg is None:
        # gnupg is not installed
        return

    if fingerprint != config_fingerprint:
        gpg = gnupg.GPG()

        # Secret key must be deleted first
        gpg.delete_keys(fingerprint, True)
        gpg.delete_keys(fingerprint)


@pytest.mark.skipif(gnupg is None, reason="requires gnupg")
def _set_sig(filename, sigfilename):
    """Creates a signature sigfilename for file filename"""

    signature = gpg.sign(filename).data

    with open(sigfilename, "w") as sigfile:
        sigfile.write(signature)


@pytest.mark.skipif(gnupg is None, reason="requires gnupg")
def test_sign():
    """Unit test for sign"""

    filename = TESTPATH + "test1.pys"
    sigfilename = filename + ".sig"

    _set_sig(filename, sigfilename)

    valid = gpg.verify(sigfilename, filename)

    assert valid

param_verify = [
    {'filename': TESTPATH + "test1.pys",
     'sigfilename': TESTPATH + "test1.pys.sig", 'valid': 1},
    {'filename': TESTPATH + "test1.pys",
     'sigfilename': TESTPATH + "test1.pys.empty", 'valid': 0},
    {'filename': TESTPATH + "test1.pys",
     'sigfilename': TESTPATH + "test1.pys.nonsense", 'valid': 0},
]


@params(param_verify)
@pytest.mark.skipif(gnupg is None, reason="requires gnupg")
def test_sign_verify(filename, sigfilename, valid):
    """Unit test for verify"""

    if valid:
        assert gpg.verify(sigfilename, filename)
    else:
        assert not gpg.verify(sigfilename, filename)
