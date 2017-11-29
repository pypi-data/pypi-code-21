#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `movesymlink` package."""

# import pytest  # until we have better tests...


import movesymlink


def test_move_symlink_exists():
    """`movesymlink.move_symlink` should exist.

    Just that.
    """
    assert hasattr(movesymlink, 'move_symlink')
