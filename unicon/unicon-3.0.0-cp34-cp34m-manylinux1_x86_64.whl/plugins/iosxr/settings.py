__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.plugins.generic.settings import GenericSettings

class IOSXRSettings(GenericSettings):

    def __init__(self):
        super().__init__()
        self.IOSXR_INIT_EXEC_COMMANDS = [
            'terminal length 0',
            'terminal width 0'
        ]
        self.IOSXR_INIT_CONFIG_COMMANDS = [
            'no logging console',
            'line console',
            'exec-timeout 0 0',
            'absolute-timeout 0',
            'session-timeout 0',
            'line default',
            'exec-timeout 0 0',
            'absolute-timeout 0',
            'session-timeout 0'
        ]
        self.SWITCHOVER_TIMEOUT = 700
        self.SWITCHOVER_COUNTER = 50
        self.RELOAD_TIMEOUT = 400

        self.INITIAL_LAUNCH_DISCOVERY_WAIT_SEC = 2
