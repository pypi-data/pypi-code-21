""" State machine for Cimc """

__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re

from unicon.plugins.cimc.patterns import CimcPatterns
from unicon.plugins.generic.statements import GenericStatements

from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement

from unicon.core.errors import SubCommandFailure, StateMachineError

patterns = CimcPatterns()
statements = GenericStatements()


class CimcStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
      shell = State('shell', patterns.prompt)
      self.add_state(shell)
