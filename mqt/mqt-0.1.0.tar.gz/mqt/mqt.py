#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals
)
from os import environ
from os import getcwd
from os.path import realpath
from os.path import dirname

TRANSIFEX_USER = 'transbot@odoo-community.org'

class Mqt(object):
    """Set the environment elements to enable the set of such elements in the
    mqt package and avoid to pass them trough all methods, here also you 
    will find the generic methods that will ."""

    BUILD_DIR = False
    """TODO"""
    PULL_REQUEST = False
    """Is this being run in a Pull request?, it is CI dependant, then to set 
    this parameter you need to enable this vrariable from your CI itself.
    
    i.e: On .travis.yml file:
        PULL_REQUEST = $TRAVIS_PULL_REQUEST"""
    LINT_CHECK = 0
    """TODO"""
    TESTS = 0
    """TODO"""
    TRANSIFEX = 0
    """TODO"""
    WEBLATE = 0
    """TODO"""
    TRAVIS_REPO_SLUG = True
    """TODO"""
    TRANSIFEX_USER = False
    """TODO"""
    BRANCH = False
    """Branch name taken from the CI itself, necessary for some automations 
    related with the branch name.
    
    i.e: On .travis.yml file:
        PULL_REQUEST = $TRAVIS_BRANCH
    """
    VERSION = False
    """Which is the odoo version where the set of odoo modules will be tested
    on"""
    PYLINT_CONFIG_FILE = False
    """Look for an environment variable whose value is the name of a proper
    configuration file for pylint  # (this file will then be expected to be
    found in the 'cfg/' folder). If such an environment variable is not found, 
    it defaults to the standard configuration file."""
    PYLINT_EXPECTED_ERRORS = False
    """Errors that you can live with but you want to explicitly silence them
    without change your .cfg configuration file, generally usefull on the WiP
    environments"""
    path = False

    def __init__(self):
        self.LINT_CHECK = environ.get('LINT_CHECK') or self.LINT_CHECK
        self.TESTS = environ.get('TESTS') or self.TESTS
        self.WEBLATE =  environ.get('WEBLATE')
        self.TRAVIS_REPO_SLUG = environ.get('TRAVIS_REPO_SLUG')
        self.TRANSIFEX_USER = environ.get('TRANSIFEX_USER') == TRANSIFEX_USER
        self.BUILD_DIR = environ.get('BUILD_DIR', [getcwd()])
        self.PULL_REQUEST = environ.get('PULL_REQUEST')
        self.BRANCH = environ.get('BRANCH')
        self.VERSION = environ.get('VERSION')
        self.PYLINT_CONFIG_FILE = environ.get('PYLINT_CONFIG_FILE',
                                              'pylint_pr.cfg')
        self.PYLINT_EXPECTED_ERRORS = environ.get('PYLINT_EXPECTED_ERRORS')
        self.path = dirname(realpath(__file__))
