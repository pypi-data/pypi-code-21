"""
Module:
    unicon.plugins.linux.statemachine

Authors:
    ATS TEAM (ats-dev@cisco.com, CSG( STEP) - India)

Description:
    This subpackage implements state machine for linux Linux
"""

from unicon.statemachine import State, StateMachine
from unicon.plugins.linux.patterns import LinuxPatterns

p = LinuxPatterns()

class LinuxStateMachine(StateMachine):
    def create(self):
        shell = State('shell', p.prompt)
        self.add_state(shell)

