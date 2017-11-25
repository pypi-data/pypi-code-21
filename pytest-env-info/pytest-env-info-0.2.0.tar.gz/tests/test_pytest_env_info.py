# -*- coding: utf-8 -*-
import sys

import pytest


def test_pytestver(testdir):
    """Make sure that our filter set the PYTEST_VER envvar."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        def test_sth():
            import os
            assert os.environ.get('PYTEST_VER') == '%s'
    """ % pytest.__version__)

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '-v'
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_sth PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_pyver(testdir):
    """Make sure that our filter set the PYTEST_PYVER envvar."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        def test_sth():
            import os
            assert os.environ.get('PYTEST_PYVER') == '%s'
    """ % '.'.join(str(v) for v in sys.version_info[:3]))

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '-v'
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_sth PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_pymajver(testdir):
    """Make sure that our filter set the PYTEST_PYMAJVER envvar."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        def test_sth():
            import os
            assert os.environ.get('PYTEST_PYMAJVER') == '%s'
    """ % str(sys.version_info[0]))

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '-v'
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_sth PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0
