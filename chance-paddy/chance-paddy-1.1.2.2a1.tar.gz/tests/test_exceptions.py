#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: tests/unit/test_exceptions.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 26.09.2017
from nose.tools import assert_equals

from paddy.exceptions import ExecutedException, CycleCancelFailedException


def test_ExecutedException_init():
    """Check if ``ExecutedException.__init__`` works
    """
    assert_equals(ExecutedException('test').error_info, 'test')


def test_ExecutedException_str():
    """Check if ``ExecutedException.__str__`` works
    """
    assert_equals(str(ExecutedException('test')), 'test')


def test_CycleCancleFailedException_init():
    """Check if ``CycleCancelFailedException.__init__`` works
    """
    assert_equals(
        CycleCancelFailedException(['test']).not_canceled_entrusts, ['test']
    )


def test_CycleCancleFailedException_str():
    """Check if ``CycleCancelFailedException.__str__`` works
    """
    assert_equals(
        str(CycleCancelFailedException(['test'])),
        "Canceled entrusts incomplete: ['test']"
    )
