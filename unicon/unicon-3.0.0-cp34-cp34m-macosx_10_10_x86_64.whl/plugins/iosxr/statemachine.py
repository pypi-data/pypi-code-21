__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.statemachine import StateMachine
from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.plugins.iosxr.statements import IOSXRStatements
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Statement, Dialog


patterns = IOSXRPatterns()
statements = IOSXRStatements()

default_commands = [statements.commit_replace_stmt]

class IOSXRSingleRpStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        enable = State('enable', patterns.enable_prompt)

        config = State('config', patterns.config_prompt)
        #config.add_state_pattern(patterns.commit_replace_prompt)

        admin = State('admin', patterns.xr_admin_prompt)

        run = State('run', patterns.xr_run_prompt)

        #login = State('login', patterns.telnet_prompt)
        #login.add_state_pattern(patterns.username_prompt)
        #login.add_state_pattern(patterns.password_prompt)

        self.add_state(enable)
        self.add_state(config)
        self.add_state(admin)
        self.add_state(run)
        #self.add_state(login)

        config_dialog = Dialog([
           [patterns.commit_changes_prompt, 'sendline(yes)', None, True, False],
           [patterns.commit_replace_prompt, 'sendline(yes)', None, True, False],
           [patterns.configuration_failed_message,
           'sendline(show configuration failed)', None, True, False]
           ])
        #login_dialog = Dialog( [
        #   [patterns.telnet_prompt, 'sendline()', None, True, False],
        #   [patterns.username_prompt, 'sendline(root)', None, True, False],
        #   [patterns.password_prompt, 'sendline(lab)', None, True, False],
        #   [patterns.commit_changes_prompt, 'sendline(no)', None, True, False],
        #   [patterns.config_prompt, 'sendline(end)', None, True, False],
        #   [patterns.logout_prompt, 'sendline()', None, True, False]] )

        enable_to_config = Path(enable, config, 'configure terminal', None)
        enable_to_admin = Path(enable, admin, 'admin', None)
        enable_to_run = Path(enable, run, 'run', None)
        admin_to_enable = Path(admin, enable, 'exit', None)
        run_to_enable = Path(run, enable, 'exit', None)
        config_to_enable = Path(config, enable, 'end', config_dialog)
        #login_to_enable = Path(login, enable, None, login_dialog)

        self.add_path(config_to_enable)
        self.add_path(enable_to_config)
        self.add_path(enable_to_admin)
        self.add_path(enable_to_run)
        self.add_path(admin_to_enable)
        self.add_path(run_to_enable)
        #self.add_path(login_to_enable)

        self.add_default_statements(default_commands)

class IOSXRDualRpStateMachine(IOSXRSingleRpStateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        super().create()

        standby_locked = State('standby_locked', patterns.standby_prompt)
        self.add_state(standby_locked)


