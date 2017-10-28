# -*- coding: utf-8 -*-

"""Utilities related to py.test"""

import uuid
import pytest


@pytest.fixture
def unique_filename():
    """Creates a UUID-based unique filename"""
    return str(uuid.uuid1())
