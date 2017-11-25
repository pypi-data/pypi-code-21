# -*- coding: utf-8 -*-
# Copyright 2017, Toshio Kuratomi
# License: MIT
#   (See https://github.com/abadger/pytest-env-info/blob/master/LICENSE)
import os
import platform

import pytest


old_VER = None
old_PYVER = None
old_PYMAJVER = None
old_PYMAJMINVER = None


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_load_initial_conftests(early_config, parser, args):
    """
    Push information about the running pytest that we can autodetect into the
    environment before any other plugin runs.  That way plugins like pytest-cov
    which use environment variables when they configure themselves can make use
    of those.

    This has to be a hookwrapper so that some plugins (pytest-cov) will have
    the environment variables set when they run.
    """
    global old_VER
    global old_PYVER
    global old_PYMAJVER
    global old_PYMAJMINVER

    old_VER = os.environ.get('PYTEST_VER', None)
    old_PYVER = os.environ.get('PYTEST_PYVER', None)
    old_PYMAJVER = os.environ.get('PYTEST_PYMAJVER', None)
    old_PYMAJMINVER = os.environ.get('PYTEST_PYMAJMINVER', None)

    os.environ['PYTEST_VER'] = pytest.__version__
    pyver = platform.python_version_tuple()
    os.environ['PYTEST_PYVER'] = '.'.join(str(v) for v in pyver)
    os.environ['PYTEST_PYMAJVER'] = str(pyver[0])
    os.environ['PYTEST_PYMAJMINVER'] = '.'.join(str(v) for v in pyver[:2])

    yield


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config):
    """
    Cleanup the environment variables we set

    (Not really needed as pytest will exit soon after)
    """
    global old_VER
    global old_PYVER
    global old_PYMAJVER
    global old_PYMAJMINVER

    if old_VER is None:
        del os.environ['PYTEST_VER']
    else:
        os.environ['PYTEST_VER'] = old_VER

    if old_PYVER is None:
        del os.environ['PYTEST_PYVER']
    else:
        os.environ['PYTEST_PYVER'] = old_PYVER

    if old_PYMAJVER is None:
        del os.environ['PYTEST_PYMAJVER']
    else:
        os.environ['PYTEST_PYMAJVER'] = old_PYMAJVER

    if old_PYMAJMINVER is None:
        del os.environ['PYTEST_PYMAJMINVER']
    else:
        os.environ['PYTEST_PYMAJMINVER'] = old_PYMAJMINVER
